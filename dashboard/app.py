import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import psycopg
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from psycopg.rows import dict_row


BASE_DIR = Path(__file__).resolve().parent
TELEMETRY_FRESHNESS_SECONDS = int(os.getenv("TELEMETRY_FRESHNESS_SECONDS", "10"))
DEFAULT_OEE_WINDOW_MINUTES = int(os.getenv("OEE_WINDOW_MINUTES", "60"))
DEFAULT_QUALITY_RATIO = float(os.getenv("OEE_DEFAULT_QUALITY_RATIO", "1.0"))
IDEAL_CYCLE_TIME_SECONDS = os.getenv("OEE_IDEAL_CYCLE_TIME_SECONDS")
app = FastAPI(title="FANUC MQTT Dashboard")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def get_connection() -> psycopg.Connection[Any]:
    return psycopg.connect(os.environ["POSTGRES_DSN"], row_factory=dict_row)


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    return None


def topic_label(topic: str) -> str:
    parts = topic.split("/")
    if len(parts) >= 2:
        return " / ".join(parts[-2:])
    return topic


def topic_key(topic: str) -> str:
    parts = topic.split("/")
    if len(parts) >= 2:
        return "/".join(parts[-2:])
    return topic


def telemetry_connectivity(last_received_at: datetime | None) -> tuple[str, str, str]:
    if last_received_at is None:
        return "No data", "muted", "No telemetry has been received yet."

    age_seconds = (datetime.now(timezone.utc) - last_received_at).total_seconds()
    detail = f"Last MQTT message received {age_seconds:.1f}s ago"
    if age_seconds <= TELEMETRY_FRESHNESS_SECONDS:
        return "Connected", "success", detail
    return "Stale", "warning", detail


def ratio_to_percent(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value * 100, 1)


def current_mode(snapshot: dict[str, dict[str, Any]]) -> str:
    if parse_bool(snapshot.get("Status/AUTO_mode", {}).get("payload_text")):
        return "AUTO"
    if parse_bool(snapshot.get("Status/T1_mode", {}).get("payload_text")):
        return "T1"
    if parse_bool(snapshot.get("Status/T2_mode", {}).get("payload_text")):
        return "T2"
    if parse_bool(snapshot.get("Status/TP_enabled", {}).get("payload_text")):
        return "TP Enabled"
    return "Unknown"


def current_phase(snapshot: dict[str, dict[str, Any]], telemetry_state: str) -> tuple[str, str]:
    alarm = parse_bool(snapshot.get("Status/Alarm", {}).get("payload_text"))
    paused = parse_bool(snapshot.get("Status/Paused", {}).get("payload_text"))
    running = parse_bool(snapshot.get("Status/Running", {}).get("payload_text"))
    program_status = snapshot.get("Status/Program_status", {}).get("payload_text") or "Unknown"

    safety_active = any(
        parse_bool(snapshot.get(key, {}).get("payload_text"))
        for key in (
            "Alarms/Estop_EXT",
            "Alarms/Estop_OP_panel",
            "Alarms/Estop_TP",
            "Alarms/Fence_Open",
            "Status/Alarm",
        )
    )

    if telemetry_state != "Connected":
        return "Telemetry stale", "warning"
    if safety_active or alarm:
        return "Safety stop", "danger"
    if paused:
        return "Paused", "warning"
    if running:
        return "Running", "success"
    if str(program_status).upper() == "ABORTED":
        return "Program aborted", "danger"
    if current_mode(snapshot) in {"T1", "T2", "TP Enabled"}:
        return "Manual / Teach", "info"
    return "Idle", "muted"


def build_flow_steps(
    snapshot: dict[str, dict[str, Any]],
    telemetry_state: str,
    telemetry_state_level: str,
    telemetry_detail: str,
) -> list[dict[str, str]]:
    controller_disconnected = parse_bool(snapshot.get("Status/Disconnected", {}).get("payload_text"))
    safety_active = any(
        parse_bool(snapshot.get(key, {}).get("payload_text"))
        for key in (
            "Alarms/Estop_EXT",
            "Alarms/Estop_OP_panel",
            "Alarms/Estop_TP",
            "Alarms/Fence_Open",
            "Status/Alarm",
        )
    )
    mode = current_mode(snapshot)
    program_status = snapshot.get("Status/Program_status", {}).get("payload_text") or "Unknown"
    running = parse_bool(snapshot.get("Status/Running", {}).get("payload_text"))
    paused = parse_bool(snapshot.get("Status/Paused", {}).get("payload_text"))
    last_cycle = snapshot.get("Status/Last_cycle_time_s", {}).get("payload_text") or "-"
    product_count = snapshot.get("Status/Total_product_amount", {}).get("payload_text") or "-"

    return [
        {
            "title": "Connectivity",
            "value": telemetry_state,
            "detail": telemetry_detail,
            "state": telemetry_state_level,
        },
        {
            "title": "Controller disconnected signal",
            "value": "True" if controller_disconnected else "False",
            "detail": "Raw value from topic Status/Disconnected",
            "state": "warning" if controller_disconnected else "success",
        },
        {
            "title": "Safety chain",
            "value": "Active safety event" if safety_active else "Safety OK",
            "detail": "Alarm and E-stop supervision",
            "state": "danger" if safety_active else "success",
        },
        {
            "title": "Operating mode",
            "value": mode,
            "detail": "AUTO / T1 / T2 / TP mode",
            "state": "info" if mode != "Unknown" else "muted",
        },
        {
            "title": "Program state",
            "value": str(program_status),
            "detail": "Current program status signal",
            "state": "danger" if str(program_status).upper() == "ABORTED" else "info",
        },
        {
            "title": "Execution",
            "value": "Running" if running else "Paused" if paused else "Stopped",
            "detail": f"Last cycle: {last_cycle}s",
            "state": "success" if running else "warning" if paused else "muted",
        },
        {
            "title": "Output",
            "value": product_count,
            "detail": "Total product amount counter",
            "state": "info",
        },
    ]


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", {"refresh_seconds": 5})


@app.get("/health")
def health() -> dict[str, str]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
    return {"status": "ok"}


@app.get("/api/summary")
def summary() -> dict[str, Any]:
    recent_since = datetime.now(timezone.utc) - timedelta(minutes=15)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_messages,
                    MAX(received_at) AS last_received_at,
                    COUNT(DISTINCT topic) AS unique_topics
                FROM mqtt_messages
                """
            )
            totals = cur.fetchone() or {}

            cur.execute(
                """
                SELECT COUNT(*) AS messages_last_15m
                FROM mqtt_messages
                WHERE received_at >= %s
                """,
                (recent_since,),
            )
            last_15m = cur.fetchone() or {}

            cur.execute(
                """
                SELECT
                    split_part(topic, '/', 2) AS site,
                    COUNT(*) AS message_count
                FROM mqtt_messages
                GROUP BY split_part(topic, '/', 2)
                ORDER BY message_count DESC
                LIMIT 10
                """
            )
            sites = cur.fetchall()

            cur.execute(
                """
                SELECT
                    topic,
                    payload_text,
                    received_at
                FROM mqtt_messages
                ORDER BY received_at DESC
                LIMIT 1
                """
            )
            latest = cur.fetchone()

    return {
        "total_messages": totals.get("total_messages", 0),
        "unique_topics": totals.get("unique_topics", 0),
        "last_received_at": totals.get("last_received_at"),
        "messages_last_15m": last_15m.get("messages_last_15m", 0),
        "top_sites": sites,
        "latest_message": latest,
    }


@app.get("/api/messages")
def messages(
    limit: int = Query(default=50, ge=1, le=500),
    topic_filter: str = Query(default=""),
) -> dict[str, Any]:
    sql = """
        SELECT
            id,
            topic,
            payload_text,
            qos,
            retain,
            received_at
        FROM mqtt_messages
    """
    params: list[Any] = []

    if topic_filter:
        sql += " WHERE topic ILIKE %s"
        params.append(f"%{topic_filter}%")

    sql += " ORDER BY received_at DESC LIMIT %s"
    params.append(limit)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

    return {"items": rows, "count": len(rows)}


@app.get("/api/topic-stats")
def topic_stats(limit: int = Query(default=15, ge=1, le=100)) -> dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    topic,
                    COUNT(*) AS message_count,
                    MAX(received_at) AS last_received_at
                FROM mqtt_messages
                GROUP BY topic
                ORDER BY message_count DESC, topic ASC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()

    return {"items": rows}


@app.get("/api/process-flow")
def process_flow() -> dict[str, Any]:
    recent_since = datetime.now(timezone.utc) - timedelta(minutes=15)
    recent_changes_since = datetime.now(timezone.utc) - timedelta(hours=6)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT MAX(received_at) AS latest_message_at
                FROM mqtt_messages
                """
            )
            telemetry_row = cur.fetchone() or {}

            cur.execute(
                """
                WITH latest AS (
                    SELECT DISTINCT ON (topic)
                        topic,
                        payload_text,
                        received_at
                    FROM mqtt_messages
                    WHERE topic LIKE '%%/Status/%%' OR topic LIKE '%%/Alarms/%%'
                    ORDER BY topic, received_at DESC
                )
                SELECT topic, payload_text, received_at
                FROM latest
                ORDER BY topic
                """
            )
            latest_status_rows = cur.fetchall()

            cur.execute(
                """
                SELECT
                    split_part(topic, '/', 6) AS category,
                    COUNT(*) AS message_count
                FROM mqtt_messages
                WHERE received_at >= %s
                GROUP BY split_part(topic, '/', 6)
                ORDER BY message_count DESC, category ASC
                """,
                (recent_since,),
            )
            cadence_rows = cur.fetchall()

            cur.execute(
                """
                WITH ordered AS (
                    SELECT
                        topic,
                        payload_text,
                        received_at,
                        LAG(payload_text) OVER (PARTITION BY topic ORDER BY received_at) AS previous_value
                    FROM mqtt_messages
                    WHERE received_at >= %s
                      AND (topic LIKE '%%/Status/%%' OR topic LIKE '%%/Alarms/%%')
                )
                SELECT
                    topic,
                    payload_text,
                    previous_value,
                    received_at
                FROM ordered
                WHERE previous_value IS DISTINCT FROM payload_text
                ORDER BY received_at DESC
                LIMIT 20
                """,
                (recent_changes_since,),
            )
            recent_changes = cur.fetchall()

            cur.execute(
                """
                SELECT
                    COUNT(*) FILTER (
                        WHERE payload_text ~ '^[0-9]+(\\.[0-9]+)?$'
                    ) AS numeric_points,
                    ROUND(AVG(payload_text::numeric) FILTER (
                        WHERE payload_text ~ '^[0-9]+(\\.[0-9]+)?$'
                    ), 2) AS avg_cycle_time_s,
                    ROUND(MAX(payload_text::numeric) FILTER (
                        WHERE payload_text ~ '^[0-9]+(\\.[0-9]+)?$'
                    ), 2) AS max_cycle_time_s,
                    ROUND(MIN(payload_text::numeric) FILTER (
                        WHERE payload_text ~ '^[0-9]+(\\.[0-9]+)?$'
                    ), 2) AS min_cycle_time_s
                FROM mqtt_messages
                WHERE topic LIKE '%%/Status/Last_cycle_time_s'
                  AND received_at >= NOW() - INTERVAL '6 hours'
                """
            )
            cycle_stats = cur.fetchone() or {}

    snapshot = {topic_key(row["topic"]): row for row in latest_status_rows}
    latest_message_at = telemetry_row.get("latest_message_at")
    telemetry_state, telemetry_state_level, telemetry_detail = telemetry_connectivity(latest_message_at)
    controller_disconnected = parse_bool(snapshot.get("Status/Disconnected", {}).get("payload_text"))
    controller_disconnect_text = "True" if controller_disconnected else "False"

    phase_name, phase_state = current_phase(snapshot, telemetry_state)
    mode = current_mode(snapshot)
    safety_ok = not any(
        parse_bool(snapshot.get(key, {}).get("payload_text"))
        for key in (
            "Alarms/Estop_EXT",
            "Alarms/Estop_OP_panel",
            "Alarms/Estop_TP",
            "Alarms/Fence_Open",
            "Status/Alarm",
        )
    )
    running = parse_bool(snapshot.get("Status/Running", {}).get("payload_text"))
    paused = parse_bool(snapshot.get("Status/Paused", {}).get("payload_text"))

    insights: list[str] = []
    if telemetry_state != "Connected":
        insights.append(f"Real telemetry connectivity is {telemetry_state.lower()} based on message freshness, not on the controller disconnect signal.")
    else:
        insights.append("Real telemetry connectivity is healthy because fresh MQTT messages are still arriving.")
    if controller_disconnected:
        insights.append("The raw MQTT signal `Status/Disconnected` is True, so this should be treated as a machine-state signal rather than broker connectivity.")
    if str(snapshot.get("Status/Program_status", {}).get("payload_text") or "").upper() == "ABORTED":
        insights.append("The current program status is ABORTED, so the process is not completing normal execution.")
    if mode in {"T1", "T2", "TP Enabled"}:
        insights.append(f"The controller is in {mode} mode, which suggests setup or teach operation rather than automatic production.")
    if safety_ok:
        insights.append("No active safety chain alarms are visible in the latest alarm snapshot.")
    if not running and not paused:
        insights.append("Execution signals show the robot is stopped rather than actively running or paused.")

    latest_status = [
        {
            **row,
            "label": topic_label(row["topic"]),
        }
        for row in latest_status_rows
    ]
    recent_changes_items = [
        {
            **row,
            "label": topic_label(row["topic"]),
        }
        for row in recent_changes
    ]

    return {
        "current_phase": phase_name,
        "current_phase_state": phase_state,
        "telemetry_connectivity": telemetry_state,
        "telemetry_connectivity_state": telemetry_state_level,
        "telemetry_connectivity_detail": telemetry_detail,
        "controller_disconnected_signal": controller_disconnect_text,
        "controller_disconnected_state": "warning" if controller_disconnected else "success",
        "mode": mode,
        "safety_state": "OK" if safety_ok else "Active safety event",
        "execution_state": "Running" if running else "Paused" if paused else "Stopped",
        "flow_steps": build_flow_steps(snapshot, telemetry_state, telemetry_state_level, telemetry_detail),
        "cadence_last_15m": cadence_rows,
        "cycle_stats": cycle_stats,
        "latest_status": latest_status,
        "recent_changes": recent_changes_items,
        "insights": insights,
    }


@app.get("/api/oee")
def oee(window_minutes: int = Query(default=DEFAULT_OEE_WINDOW_MINUTES, ge=5, le=1440)) -> dict[str, Any]:
    window_since = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
    ideal_cycle_from_env = float(IDEAL_CYCLE_TIME_SECONDS) if IDEAL_CYCLE_TIME_SECONDS else None

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COUNT(*) AS running_samples,
                    COUNT(*) FILTER (WHERE payload_text = 'True') AS running_true_samples,
                    COUNT(*) FILTER (WHERE payload_text = 'False') AS running_false_samples,
                    MAX(received_at) AS last_running_sample_at
                FROM mqtt_messages
                WHERE topic LIKE '%%/Status/Running'
                  AND received_at >= %s
                """,
                (window_since,),
            )
            running_stats = cur.fetchone() or {}

            cur.execute(
                """
                SELECT
                    COUNT(*) AS paused_samples,
                    COUNT(*) FILTER (WHERE payload_text = 'True') AS paused_true_samples
                FROM mqtt_messages
                WHERE topic LIKE '%%/Status/Paused'
                  AND received_at >= %s
                """,
                (window_since,),
            )
            paused_stats = cur.fetchone() or {}

            cur.execute(
                """
                SELECT
                    COUNT(*) AS disconnected_samples,
                    COUNT(*) FILTER (WHERE payload_text = 'True') AS disconnected_true_samples
                FROM mqtt_messages
                WHERE topic LIKE '%%/Status/Disconnected'
                  AND received_at >= %s
                """,
                (window_since,),
            )
            disconnected_stats = cur.fetchone() or {}

            cur.execute(
                """
                SELECT
                    COUNT(*) FILTER (
                        WHERE payload_text ~ '^[0-9]+(\\.[0-9]+)?$'
                    ) AS numeric_cycle_samples,
                    COUNT(*) FILTER (
                        WHERE payload_text ~ '^[0-9]+(\\.[0-9]+)?$'
                          AND payload_text::numeric > 0
                    ) AS positive_cycle_samples,
                    ROUND(AVG(payload_text::numeric) FILTER (
                        WHERE payload_text ~ '^[0-9]+(\\.[0-9]+)?$'
                          AND payload_text::numeric > 0
                    ), 3) AS avg_positive_cycle_time_s,
                    ROUND(MIN(payload_text::numeric) FILTER (
                        WHERE payload_text ~ '^[0-9]+(\\.[0-9]+)?$'
                          AND payload_text::numeric > 0
                    ), 3) AS best_observed_cycle_time_s,
                    ROUND(MAX(payload_text::numeric) FILTER (
                        WHERE payload_text ~ '^[0-9]+(\\.[0-9]+)?$'
                          AND payload_text::numeric > 0
                    ), 3) AS worst_observed_cycle_time_s
                FROM mqtt_messages
                WHERE topic LIKE '%%/Status/Last_cycle_time_s'
                  AND received_at >= %s
                """,
                (window_since,),
            )
            cycle_stats = cur.fetchone() or {}

            cur.execute(
                """
                SELECT
                    MAX(received_at) AS last_received_at
                FROM mqtt_messages
                """
            )
            telemetry = cur.fetchone() or {}

            cur.execute(
                """
                WITH latest AS (
                    SELECT DISTINCT ON (topic)
                        topic,
                        payload_text,
                        received_at
                    FROM mqtt_messages
                    WHERE topic LIKE '%%/Status/%%' OR topic LIKE '%%/Alarms/%%'
                    ORDER BY topic, received_at DESC
                )
                SELECT topic, payload_text, received_at
                FROM latest
                ORDER BY topic
                """
            )
            latest_status_rows = cur.fetchall()

    snapshot = {topic_key(row["topic"]): row for row in latest_status_rows}
    telemetry_state, telemetry_state_level, telemetry_detail = telemetry_connectivity(telemetry.get("last_received_at"))

    running_samples = running_stats.get("running_samples") or 0
    running_true_samples = running_stats.get("running_true_samples") or 0
    paused_true_samples = paused_stats.get("paused_true_samples") or 0
    disconnected_true_samples = disconnected_stats.get("disconnected_true_samples") or 0
    positive_cycle_samples = cycle_stats.get("positive_cycle_samples") or 0
    avg_positive_cycle_time = cycle_stats.get("avg_positive_cycle_time_s")
    best_cycle_time = cycle_stats.get("best_observed_cycle_time_s")

    availability_ratio = (running_true_samples / running_samples) if running_samples else 0.0

    reference_cycle_time = ideal_cycle_from_env or best_cycle_time
    if reference_cycle_time and avg_positive_cycle_time:
        performance_ratio = min(float(reference_cycle_time) / float(avg_positive_cycle_time), 1.0)
        performance_reason = "Computed from average positive cycle time against the reference cycle."
    elif running_true_samples == 0 or positive_cycle_samples == 0:
        performance_ratio = 0.0
        performance_reason = "No positive running/cycle samples were observed in the selected window."
    else:
        performance_ratio = None
        performance_reason = "Performance could not be estimated from the available cycle data."

    quality_ratio = DEFAULT_QUALITY_RATIO
    quality_reason = "Quality is assumed because no good/scrap counter is available in the MQTT payloads."

    oee_ratio = None
    if performance_ratio is not None:
        oee_ratio = availability_ratio * performance_ratio * quality_ratio

    phase_name, _ = current_phase(snapshot, telemetry_state)
    flow_steps = build_flow_steps(snapshot, telemetry_state, telemetry_state_level, telemetry_detail)

    losses = [
        {"label": "Stop loss", "value_pct": round((1 - availability_ratio) * 100, 1)},
        {"label": "Speed loss", "value_pct": round((1 - (performance_ratio or 0.0)) * 100, 1)},
        {"label": "Quality loss", "value_pct": round((1 - quality_ratio) * 100, 1)},
    ]

    assumptions = [
        f"Observation window: last {window_minutes} minutes.",
        f"Availability is estimated from the share of `Status/Running=True` samples within the window ({running_true_samples}/{running_samples}).",
        quality_reason,
    ]
    if ideal_cycle_from_env:
        assumptions.append(f"Reference cycle time is fixed from configuration: {ideal_cycle_from_env}s.")
    elif best_cycle_time:
        assumptions.append(f"Reference cycle time uses the best observed positive cycle in the window: {best_cycle_time}s.")
    else:
        assumptions.append("No positive cycle time was observed, so performance falls back to 0%.")

    return {
        "window_minutes": window_minutes,
        "current_phase": phase_name,
        "telemetry_connectivity": telemetry_state,
        "telemetry_connectivity_detail": telemetry_detail,
        "oee_pct": ratio_to_percent(oee_ratio),
        "availability_pct": ratio_to_percent(availability_ratio),
        "performance_pct": ratio_to_percent(performance_ratio),
        "quality_pct": ratio_to_percent(quality_ratio),
        "performance_reason": performance_reason,
        "quality_reason": quality_reason,
        "reference_cycle_time_s": reference_cycle_time,
        "avg_positive_cycle_time_s": avg_positive_cycle_time,
        "best_observed_cycle_time_s": best_cycle_time,
        "worst_observed_cycle_time_s": cycle_stats.get("worst_observed_cycle_time_s"),
        "positive_cycle_samples": positive_cycle_samples,
        "numeric_cycle_samples": cycle_stats.get("numeric_cycle_samples") or 0,
        "running_true_samples": running_true_samples,
        "running_false_samples": running_stats.get("running_false_samples") or 0,
        "paused_true_samples": paused_true_samples,
        "disconnected_true_samples": disconnected_true_samples,
        "losses": losses,
        "assumptions": assumptions,
        "flow_steps": flow_steps,
    }

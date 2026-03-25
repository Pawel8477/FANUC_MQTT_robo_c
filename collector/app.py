import json
import logging
import os
import ssl
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import paho.mqtt.client as mqtt
import psycopg
from psycopg.types.json import Json


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("fanuc-collector")


@dataclass(frozen=True)
class Settings:
    pg_dsn: str
    mqtt_host: str
    mqtt_port: int
    mqtt_topic: str
    mqtt_client_id: str
    mqtt_keepalive: int
    mqtt_ca_cert: str
    mqtt_client_cert: str
    mqtt_client_key: str
    mqtt_insecure_hostname: bool


def load_settings() -> Settings:
    return Settings(
        pg_dsn=os.environ["POSTGRES_DSN"],
        mqtt_host=os.getenv("MQTT_HOST", "fanuc-iot.eu"),
        mqtt_port=int(os.getenv("MQTT_PORT", "443")),
        mqtt_topic=os.getenv("MQTT_TOPIC", "FANUC-PL/#"),
        mqtt_client_id=os.getenv("MQTT_CLIENT_ID", "fanuc-mqtt-collector"),
        mqtt_keepalive=int(os.getenv("MQTT_KEEPALIVE", "60")),
        mqtt_ca_cert=os.environ["MQTT_CA_CERT"],
        mqtt_client_cert=os.environ["MQTT_CLIENT_CERT"],
        mqtt_client_key=os.environ["MQTT_CLIENT_KEY"],
        mqtt_insecure_hostname=os.getenv("MQTT_INSECURE_HOSTNAME", "true").lower() == "true",
    )


class MessageStore:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._conn: psycopg.Connection[Any] | None = None

    def connect(self) -> None:
        self._conn = psycopg.connect(self._dsn, autocommit=True)
        logger.info("Connected to PostgreSQL")

    def insert_message(
        self,
        topic: str,
        payload_bytes: bytes,
        qos: int,
        retain: bool,
        received_at: datetime,
    ) -> None:
        if self._conn is None or self._conn.closed:
            self.connect()

        payload_text = payload_bytes.decode("utf-8", errors="replace")
        payload_json = None
        try:
            payload_json = json.loads(payload_text)
        except json.JSONDecodeError:
            payload_json = None

        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO mqtt_messages (
                    topic,
                    payload_text,
                    payload_bytes,
                    payload_json,
                    qos,
                    retain,
                    received_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    topic,
                    payload_text,
                    payload_bytes,
                    Json(payload_json) if payload_json is not None else None,
                    qos,
                    retain,
                    received_at,
                ),
            )


def wait_for_postgres(store: MessageStore) -> None:
    delay_seconds = 2
    while True:
        try:
            store.connect()
            return
        except Exception as exc:  # noqa: BLE001
            logger.warning("PostgreSQL not ready yet: %s", exc)
            time.sleep(delay_seconds)


def build_mqtt_client(settings: Settings, store: MessageStore) -> mqtt.Client:
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=settings.mqtt_client_id,
        protocol=mqtt.MQTTv311,
    )

    tls_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=settings.mqtt_ca_cert)
    tls_context.load_cert_chain(
        certfile=settings.mqtt_client_cert,
        keyfile=settings.mqtt_client_key,
    )
    tls_context.check_hostname = not settings.mqtt_insecure_hostname

    client.tls_set_context(tls_context)
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    def on_connect(
        client: mqtt.Client,
        userdata: Any,
        flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        logger.info("Connected to MQTT broker with result code %s", reason_code)
        client.subscribe(settings.mqtt_topic, qos=0)
        logger.info("Subscribed to topic %s", settings.mqtt_topic)

    def on_disconnect(
        client: mqtt.Client,
        userdata: Any,
        disconnect_flags: mqtt.DisconnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        logger.warning("Disconnected from MQTT broker with result code %s", reason_code)

    def on_message(client: mqtt.Client, userdata: Any, msg: mqtt.MQTTMessage) -> None:
        received_at = datetime.now(timezone.utc)
        store.insert_message(
            topic=msg.topic,
            payload_bytes=msg.payload,
            qos=msg.qos,
            retain=bool(msg.retain),
            received_at=received_at,
        )
        logger.info("Stored message topic=%s bytes=%s", msg.topic, len(msg.payload))

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    return client


def main() -> None:
    settings = load_settings()
    store = MessageStore(settings.pg_dsn)
    wait_for_postgres(store)

    client = build_mqtt_client(settings, store)

    logger.info("Connecting to MQTT broker %s:%s", settings.mqtt_host, settings.mqtt_port)
    client.connect(settings.mqtt_host, settings.mqtt_port, settings.mqtt_keepalive)
    client.loop_forever()


if __name__ == "__main__":
    main()

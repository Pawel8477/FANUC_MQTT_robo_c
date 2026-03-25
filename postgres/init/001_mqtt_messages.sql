CREATE TABLE IF NOT EXISTS mqtt_messages (
    id BIGSERIAL PRIMARY KEY,
    topic TEXT NOT NULL,
    payload_text TEXT,
    payload_bytes BYTEA NOT NULL,
    payload_json JSONB,
    qos SMALLINT NOT NULL,
    retain BOOLEAN NOT NULL DEFAULT FALSE,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mqtt_messages_topic ON mqtt_messages (topic);
CREATE INDEX IF NOT EXISTS idx_mqtt_messages_received_at ON mqtt_messages (received_at DESC);

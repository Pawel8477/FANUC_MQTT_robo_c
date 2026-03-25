# FANUC MQTT -> PostgreSQL + Dashboard

Lokalny stack do odbierania danych z MQTT partnera, zapisu surowych wiadomosci do PostgreSQL i podgladu przez dashboard webowy.

## Co zawiera

- `collector` - klient MQTT z mTLS zapisujacy wiadomosci do tabeli `mqtt_messages`
- `postgres` - baza danych PostgreSQL 16
- `dashboard` - webowy panel z podsumowaniem i lista ostatnich wiadomosci

## Wymagania

- zainstalowany runtime kontenerow: Docker Desktop, Colima + Docker CLI albo Podman z compose
- lokalne certyfikaty partnera:
  - `ca.crt`
  - `DBR77.crt`
  - `DBR77.key`

## Szybki start

1. Skopiuj konfiguracje:

```bash
cp .env.example .env
```

2. Uruchom stack:

```bash
docker compose up -d --build
```

3. Podejrzyj logi collectora:

```bash
docker compose logs -f collector
```

4. Otworz dashboard:

```bash
open http://localhost:8080
```

5. Sprawdz, czy dane trafiaja do PostgreSQL:

```bash
docker compose exec postgres psql -U fanuc -d fanuc -c "SELECT id, topic, payload_text, received_at FROM mqtt_messages ORDER BY id DESC LIMIT 20;"
```

## Uwagi

- Broker odpowiada na `fanuc-iot.eu:443`.
- Certyfikat serwera jest obecnie wystawiony na inna nazwe hosta niz endpoint, dlatego domyslnie ustawione jest `MQTT_INSECURE_HOSTNAME=true`.
- Dashboard jest wystawiony lokalnie na porcie `8080` i czyta dane bezposrednio z PostgreSQL.
- Po stronie PostgreSQL zapisywane sa:
  - topic
  - payload jako tekst
  - payload jako `bytea`
  - payload jako `jsonb`, jesli wiadomo go sparsowac
  - qos, retain i znaczniki czasu

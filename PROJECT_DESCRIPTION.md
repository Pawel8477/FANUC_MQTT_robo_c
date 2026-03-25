# FANUC MQTT Robo C

Projekt integruje dane MQTT z robota FANUC i zapisuje je lokalnie do PostgreSQL, a nastepnie udostepnia w dashboardzie webowym.

## Zakres projektu

- collector MQTT z autoryzacja mTLS
- zapis surowych wiadomosci do PostgreSQL
- dashboard webowy z trzema panelami:
  - `Overview`
  - `Process Flow`
  - `Process & OEE`
- eksport zebranych danych do XML

## Architektura

```text
FANUC MQTT broker -> collector -> PostgreSQL -> dashboard webowy
```

## Glowne komponenty

- `collector/` - klient MQTT zapisujacy dane do tabeli `mqtt_messages`
- `postgres/` - inicjalizacja bazy danych
- `dashboard/` - aplikacja FastAPI + frontend HTML/CSS/JS
- `docker-compose.yml` - lokalny stack kontenerow

## Dane i analiza

Dashboard udostepnia:

- podglad ostatnich wiadomosci MQTT
- statystyki topicow i lokalizacji
- analize procesu na podstawie statusow i alarmow
- rozdzielenie prawdziwej lacznosci telemetrii od sygnalu `Status/Disconnected`
- estymowane OEE z aktualnie dostepnych sygnalow

## Bezpieczenstwo

Do repozytorium nie sa dodawane:

- certyfikaty klienta i CA
- plik `.env`
- eksporty danych

Sa one wykluczone przez `.gitignore`.

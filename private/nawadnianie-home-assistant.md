# Nawadnianie — Dingtian DTWONDER 8CH → Home Assistant (MQTT przez WiFi)

Sterownik 8-strefowego nawadniania oparty o płytkę przekaźnikową Dingtian DTWONDER,
łączącą się z Home Assistant przez **WiFi + MQTT**.

## Jak to działa
- Każdy przekaźnik = jeden zawór elektromagnetyczny (NC): **ON = woda leci**.
- Strefy podlewane są **po kolei** (nie wszystkie naraz) — żeby starczyło ciśnienia/wody.
- O ustawionej godzinie startu uruchamia się sekwencja, jeśli `Nawadnianie aktywne`
  jest włączone i nie ma `Blokady (deszcz)`.

---

## Krok 1 — Podłączenie płytki do WiFi (tryb STA)
Domyślnie płytka działa jako własny hotspot. Trzeba ją przełączyć na Twoją sieć:
1. Połącz telefon/laptop z WiFi płytki: SSID `dtrelaySN`, hasło `dtpassword`.
2. Otwórz panel `http://192.168.7.1` (login `admin` / `admin`).
3. Wejdź w **WiFi / Network** → tryb **STA (Station)** → wybierz swoją domową sieć
   i wpisz hasło. Zapisz i zresetuj.
4. Płytka dostanie IP z routera (DHCP). **Zarezerwuj jej stałe IP** w routerze
   (po adresie MAC), żeby się nie zmieniało.

## Krok 2 — Broker MQTT w Home Assistant
1. Settings → Add-ons → zainstaluj i uruchom **Mosquitto broker** („Start on boot").
2. Settings → Devices & Services → dodaj integrację **MQTT**.
3. Załóż użytkownika MQTT (np. `ha` + hasło) dla płytki.

## Krok 3 — Konfiguracja MQTT na płytce
W panelu płytki → zakładka **MQTT**:
- Broker: **IP Home Assistanta** (u nas `192.168.8.50`), port `1883`
- User / Password: jak w Mosquitto
- Włącz publikowanie stanu przekaźników
- Ustaw topici zgodnie z packagem:
  - komenda: `dingtian/relay01/relay/r{N}/set`  (payload `ON`/`OFF`)
  - stan:    `dingtian/relay01/relay/r{N}`
  - LWT/availability: `dingtian/relay01/availability` (`online`/`offline`)

## Krok 4 — Wgranie wsadu do HA
1. Skopiuj `packages/nawadnianie.yaml` do `/config/packages/`.
2. W `configuration.yaml` upewnij się, że masz:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```
3. Developer Tools → **Check configuration** → **Restart**.
4. Dodaj kartę z `lovelace_nawadnianie.yaml` na dashboard.

## Krok 5 — Weryfikacja
Podejrzyj ruch MQTT (z maszyny z `mosquitto-clients`):
```bash
mosquitto_sub -h 192.168.8.50 -u ha -P <hasło> -t '#' -v
```
Włącz „Strefę 1" w HA → na brokerze powinna pojawić się komenda, a płytka odeśle stan.

---

## ⚠️ Ważne dla nawadniania
- **Sprawdź payloady firmware.** Część wersji Dingtiana publikuje JSON, nie `ON/OFF`.
  Jeśli stan się nie odświeża — podejrzyj `mosquitto_sub` i dorób `value_template`.
- **Bezpiecznik czasu.** Każda strefa wyłącza się po ustawionym czasie. Skrypt ma
  `mode: restart`, więc ponowne uruchomienie nie zostawi otwartego zaworu.
- **STOP awaryjny** (`script.nawadnianie_stop`) zamyka wszystkie zawory naraz.
- **Zasilanie zaworów:** typowe cewki 24 V AC podłącz do COM/NO przekaźnika
  przez własny transformator — płytka tylko przełącza, nie zasila cewek z siebie.
- Rozważ czujnik deszczu/wilgotności gleby podpięty pod
  `input_boolean.nawadnianie_blokada_deszcz`.

---

## Konfiguracja — `packages/nawadnianie.yaml`
Plik dostępny osobno w `private/packages/nawadnianie.yaml`. Zawiera:
- `mqtt.switch` × 8 — strefy (zawory)
- `input_number` × 8 — czas podlewania per strefa (0 = pomiń)
- `input_boolean` — master + blokada (deszcz)
- `input_datetime` — godzina startu
- `script.nawadnianie_sekwencja` — sekwencyjne podlewanie wg czasów
- `script.nawadnianie_stop` — awaryjne wyłączenie wszystkiego
- `automation` — start o godzinie + alarm gdy sterownik offline

## Dashboard — `lovelace_nawadnianie.yaml`
Karta z sterowaniem (master, blokada, godzina, start/stop), podglądem stanu
8 stref oraz suwakami czasów. Wklej w trybie YAML edytora dashboardu.

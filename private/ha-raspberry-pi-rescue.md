# Home Assistant OS (Raspberry Pi) nie odpowiada — ratunek i reinstalacja

## A. Najpierw SZYBKA DIAGNOSTYKA (zanim zaorasz — 5 min)

Najczęściej HA "nie odpowiada", a wcale nie trzeba go stawiać na nowo.

1. **Dioda i zasilanie RPi**
   - Czerwona = zasilanie OK. Brak zielonej migającej = nie czyta karty SD (częsta sprawa!).
   - Użyj **dobrego zasilacza 5V/3A** — słaby zasilacz = losowe zwiechy.

2. **Sieć / adres**
   - Spróbuj kolejno w przeglądarce:
     - `http://homeassistant.local:8123`
     - `http://homeassistant:8123`
     - `http://<IP_RPI>:8123` (IP sprawdź w routerze, lista klientów DHCP)
   - Pinguj: `ping homeassistant.local`  → jeśli odpowiada, to tylko web/HA core wisi.

3. **Daj mu czas** — po restarcie/aktualizacji HA potrafi wstawać **5–10 min**.
   Strona `8123` może pokazywać „Home Assistant is starting…".

4. **Konsola/monitor** — podłącz HDMI do RPi. Jeśli widać logowanie `ha >`:
   ```
   ha core info          # stan core
   ha core start         # wystartuj core
   ha core logs          # zobacz błąd (zwykle błąd w configuration.yaml)
   ha supervisor logs
   ha host reboot        # twardy restart
   ```
   90% przypadków „nie wstaje po edycji YAML" = literówka w configu → `ha core logs` pokaże którą linię.

5. **Karta SD** — to najczęstsza przyczyna śmierci HA OS.
   Jeśli RPi w ogóle nie bootuje → karta padła (tanie SD nie znoszą ciągłego zapisu).
   Przejdź do sekcji B i przy okazji **przejdź na dysk SSD/USB albo dobrą kartę** (np. SanDisk Max Endurance).

> Masz backup? HA domyślnie robi snapshoty w `/config/backups` i (jeśli włączone) Google Drive.
> Jeśli tak — reinstalacja jest bezbolesna (sekcja C).

---

## B. REINSTALACJA HA OS na Raspberry Pi (od zera)

Potrzebne: czytnik kart / dysk USB-SSD, **Raspberry Pi Imager** (https://www.raspberrypi.com/software/).

1. **Pobierz obraz**: w Imagerze wybierz
   `Choose OS → Other specific-purpose OS → Home Assistants and home automation → Home Assistant → Home Assistant OS` (wybierz wariant pod swój model RPi, np. RPi 4 / RPi 5).
2. **Wybierz nośnik** (karta SD lub — zalecane — SSD/USB).
3. **Zapisz** (Write) i włóż do RPi, podłącz **LAN kablem** na czas instalacji (pewniej niż WiFi).
4. Włącz RPi, odczekaj ~5–10 min, wejdź na `http://homeassistant.local:8123`.
5. Ekran powitalny:
   - **Jeśli masz backup** → kliknij małe „**Restore from backup**" i wgraj plik `.tar` (sekcja C2).
   - Jeśli nie → załóż konto i odtwórz konfigurację ręcznie (sekcja C3).

> Wskazówka na przyszłość: **Settings → System → Backups → Automatic backups** + kopia na Google Drive (dodatek „Home Assistant Google Drive Backup"). To ratuje życie.

---

## C. Przywrócenie środowiska + nawadnianie

### C1. Po starcie HA — dodatki bazowe
- Settings → Add-ons → **Mosquitto broker** (zainstaluj, Start, „Start on boot").
- Settings → Devices & Services → dodaj integrację **MQTT**.
- (opcjonalnie) **File editor** lub **Studio Code Server** — do wgrania YAML.
- Załóż użytkownika MQTT (np. `ha` + hasło) dla płytki Dingtian.

### C2. Restore z backupu (jeśli był)
Settings → System → Backups → **Upload backup** → wybierz `.tar` → Restore (full).
To przywróci configuration.yaml, packages, automatyzacje, dashboard — wszystko.

### C3. Jeśli budujesz config na nowo — wgraj nasze nawadnianie
1. Wrzuć `packages/nawadnianie.yaml` do `/config/packages/`.
2. W `/config/configuration.yaml`:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```
3. Developer Tools → **Check configuration** → **Restart**.
4. Dodaj kartę z `lovelace_nawadnianie.yaml` na dashboard.
5. Na płytce Dingtian ustaw broker MQTT na **IP nowego HA** (po reinstalacji IP mogło się zmienić — najlepiej zarezerwuj stałe IP RPi w routerze).

### C4. Weryfikacja
```bash
mosquitto_sub -h <IP_HA> -u ha -P <hasło> -t '#' -v
```
Włącz „Strefę 1" → na brokerze pojawia się komenda, płytka odsyła stan.

---

## Checklista „żeby się nie powtórzyło"
- [ ] HA na **SSD/USB** zamiast taniej karty SD
- [ ] **Stałe IP** dla RPi i dla płytki Dingtian (rezerwacja w routerze po MAC)
- [ ] **Automatyczne backupy** + kopia poza RPi (Google Drive)
- [ ] Zasilacz **5V/3A** dobrej jakości
- [ ] Po każdej edycji YAML: **Check configuration** PRZED restartem

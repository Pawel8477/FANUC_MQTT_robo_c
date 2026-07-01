# Smart Home — dokumentacja (private)

Zbiór notatek i konfiguracji do domowego nawadniania opartego o Home Assistant
i 8-kanałową płytkę przekaźnikową **Dingtian DTWONDER**.

## Spis treści
| Plik | Co zawiera |
|------|-----------|
| `nawadnianie-home-assistant.md` | Główny przewodnik: integracja płytki przez MQTT/WiFi + cała logika nawadniania (z configami) |
| `packages/nawadnianie.yaml` | Gotowy HA package — 8 stref, czasy, harmonogram, sekwencja, STOP |
| `lovelace_nawadnianie.yaml` | Karta na dashboard (sterowanie + stan stref + czasy) |
| `ha-raspberry-pi-rescue.md` | Ratunek i reinstalacja Home Assistant OS na Raspberry Pi |
| `dell-9020-no-boot.md` | Diagnostyka Dell 9020 „No bootable devices found" + postawienie HA na tym sprzęcie |

## Sprzęt
- **Sterownik:** Dingtian DTWONDER, 8× przekaźnik (NC/COM/NO) + 8× wejście (I1–I8)
- **Łączność:** WiFi (tryb STA) → MQTT do Home Assistant
- **Panel płytki:** `admin` / `admin` — AP `192.168.7.1` (`dtrelaySN` / `dtpassword`) lub ETH `192.168.1.100`
- **Serwer HA:** Dell 9020 (x86-64)

## Status (dziennik)
- [x] Zidentyfikowano płytkę Dingtian DTWONDER i przygotowano wsad MQTT
- [x] Przerobiono wsad pod **nawadnianie 8 stref** (po WiFi)
- [x] Diagnostyka serwera HA — pierwotnie HA OS na Raspberry Pi „nie odpowiadał"
- [x] Przeniesiono serwer na **Dell 9020**; „No bootable devices found" = zły **Boot Mode**
- [x] **Naprawione:** przełączenie BIOS na **UEFI** → system ruszył z dysku
- [x] HA wstał, adres w sieci lokalnej: **`http://192.168.8.50:8123`**
- [x] **Potwierdzone (2026-06-30):** panel HA się ładuje — `HTTP 200`, ~4 ms z Maca
- [x] **Reset hasła ownera** przez konsolę HAOS (Dell), ponowne logowanie OK
- [x] **Mosquitto broker** zainstalowany + uruchomiony (start przy starcie); port `1883` otwarty ✅ (2026-07-01)
- [x] **Integracja MQTT** dodana (broker `core-mosquitto` z dodatku)
- [x] **Wgrano wsad** — plik jako `/config/nawadnianie.yaml`, w `configuration.yaml` dodano `homeassistant: packages: { nawadnianie: !include nawadnianie.yaml }`. `check_config` → **valid**, po restarcie encje wczytane
- [x] **Encje działają** — 8× `switch.strefa_N`, 8× `input_number`, `input_boolean` (master/blokada), `input_datetime`, 2 skrypty, 2 automatyzacje. Strefy `unavailable` (płytka offline — oczekiwane)
- [x] **Dashboard** — osobny panel „Nawadnianie" (`/nawadnianie-panel/main`, w pasku bocznym): sterowanie + stan stref + suwaki czasów
- [ ] Ustawić na płytce Dingtian broker = `192.168.8.50`, zarezerwować stałe IP w routerze — *płytka wciąż nieosiągalna (skan `/24` bez płytki), do zasilenia/podłączenia do WiFi*
- [ ] Zweryfikować ruch MQTT i przetestować strefy (po podłączeniu płytki)

> **Ważne (poprawka wdrożeniowa):** blok `device:` powodował długie `entity_id`
> (`switch.nawadnianie_dingtian_8ch_strefa_N`). Do każdego przełącznika dodano
> **`object_id: strefa_N`**, żeby `entity_id` = `switch.strefa_N` (zgodne ze skryptami,
> automatyzacjami i dashboardem). Wdrożone encje dodatkowo przemianowano w rejestrze.

### Diagnostyka sieci (2026-06-30, z Maca `192.168.8.29`)
| Cel | Wynik |
|-----|-------|
| `192.168.8.50:8123` (panel HA) | ✅ `HTTP 200`, ~4 ms |
| `192.168.8.50:4357` (HAOS Observer) | ✅ otwarty → to **Home Assistant OS** z Supervisorem (add-ony dostępne) |
| `192.168.8.50:1883` (Mosquitto/MQTT) | ❌ zamknięty → broker jeszcze nie postawiony |
| `192.168.8.50:22` (SSH) / `:445` (Samba) | ❌ zamknięte → brak ścieżki sieciowej do `/config` |
| Płytka Dingtian | ❌ **nie ma jej w sieci** — skan całego `192.168.8.0/24` (11 żywych hostów) nie pokazał panelu płytki; `.49` = serwer Ubuntu (lighttpd), `.211` = panel innego urządzenia, `.1` = router. Płytka niezasilona lub niedołączona do WiFi → krok fizyczny |

## Następny krok — **została już tylko płytka**
Cała strona HA gotowa (broker, integracja, wsad, encje, dashboard). Zostało fizyczne podłączenie sterownika:
1. **Zasil płytkę Dingtian** i podłącz ją do WiFi (tryb STA — patrz `nawadnianie-home-assistant.md`, Krok 1).
2. Namierz jej IP (panel routera / skan sieci) i **zarezerwuj stałe IP** po MAC.
3. W panelu płytki (zakładka **MQTT**): broker `192.168.8.50`, port `1883`, user/hasło jak w Mosquitto, topici zgodne z packagem (`dingtian/relay01/relay/r{N}` + `.../availability`).
4. **Test** z Maca: `mosquitto_sub -h 192.168.8.50 -u ha -P <hasło> -t '#' -v`, potem w panelu „Nawadnianie" włącz „Strefę 1" — na brokerze powinna pojawić się komenda, a strefy zmienią stan z `unavailable` na `off/on`.

> Uwaga: gdy płytka będzie online, encje `switch.strefa_N` same wyjdą z `unavailable`
> (mają `availability_topic` na LWT). Dopóki jest offline — to normalne, że pokazują „niedostępny".

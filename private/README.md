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
- [x] **Helpery/skrypty/automatyzacje/dashboard** wczytane — panel „Nawadnianie" (`/nawadnianie-panel/main`)
- [x] **Samba share** (2026-07-01) — dodatek dla folderów HA na SSD (`config/media/share/backup…`), login `homeassistant`. HDD 1 TB zostawiony (HAOS nie udostępnia osobnego dysku przez Sambę)
- [x] **Płytka Dingtian podłączona** (2026-07-01) — po **Ethernecie**, IP **`192.168.8.51`** (panel `admin`/`admin`)
- [x] **MQTT na płytce** — broker `192.168.8.50:1883`, TLS off, Head‑slash on, login **`dingtian`** (dodany w Mosquitto → Logins), MFR `dingtian`, Area `relay01`
- [x] **HA MQTT Discovery** (przycisk „HA Discover" w panelu płytki) — auto‑utworzone `switch.dingtian_relay63699_r1..8` (żywe) + `binary_sensor…_i1..8` (8 wejść)
- [x] **Encje działają na sprzęcie** — wykryte przełączniki **przemianowano na `switch.strefa_1..8`** (rename w rejestrze), stan `off`/available. Skrypty/automatyzacje/dashboard działają na realnych przekaźnikach
- [ ] Test end‑to‑end „na mokro" (fizyczne otwarcie zaworu) — do zrobienia świadomie, gdy podłączone woda/zawory
- [ ] (opcjonalnie) zarezerwować stałe IP `.51` po MAC w routerze; ustawić czasy stref + godzinę startu

> **Zmiana podejścia (2026-07-01):** zrezygnowano z ręcznych `mqtt: switch:` w pakiecie
> (zgadywane topici się nie pokrywały z firmware). Zamiast tego płytka publikuje encje
> przez **HA MQTT Discovery**, a te przemianowano na `switch.strefa_N`. Pakiet zawiera już
> tylko helpery + skrypty + automatyzacje + dashboard.
> **Loginy MQTT/Samba** (do zmiany): broker `dingtian`/`Dingtian7z-Mqtt`, Samba `homeassistant`/`Nawadn-Str8-Kq72xz`.

### Diagnostyka sieci (2026-06-30, z Maca `192.168.8.29`)
| Cel | Wynik |
|-----|-------|
| `192.168.8.50:8123` (panel HA) | ✅ `HTTP 200`, ~4 ms |
| `192.168.8.50:4357` (HAOS Observer) | ✅ otwarty → to **Home Assistant OS** z Supervisorem (add-ony dostępne) |
| `192.168.8.50:1883` (Mosquitto/MQTT) | ❌ zamknięty → broker jeszcze nie postawiony |
| `192.168.8.50:22` (SSH) / `:445` (Samba) | ❌ zamknięte → brak ścieżki sieciowej do `/config` |
| Płytka Dingtian | ❌ **nie ma jej w sieci** — skan całego `192.168.8.0/24` (11 żywych hostów) nie pokazał panelu płytki; `.49` = serwer Ubuntu (lighttpd), `.211` = panel innego urządzenia, `.1` = router. Płytka niezasilona lub niedołączona do WiFi → krok fizyczny |

## Stan: **system kompletny i działa** ✅
Broker + integracja MQTT + płytka (Discovery) + helpery/skrypty/automatyzacje + dashboard + Samba.
`switch.strefa_1..8` są żywe (`off`) i sterują realnymi przekaźnikami.

### Co zostało (drobne / świadome)
1. **Test „na mokro"** — włączenie strefy fizycznie otworzy zawór. Zrób to świadomie, gdy podłączone woda/zawory (w panelu „Nawadnianie" → „Uruchom teraz" albo przełącz `switch.strefa_1`).
2. **Ustaw czasy stref + godzinę startu** (np. 6:00) i włącz „Nawadnianie aktywne".
3. **Zarezerwuj stałe IP `.51`** po MAC w routerze (żeby się nie zmieniło).
4. **Zmień hasła** MQTT/Samba (patrz notka wyżej) — są w historii czatu.

### Wejścia (bonus)
Discovery dało też `binary_sensor.dingtian_relay63699_i1..8` (8 wejść płytki) — można podpiąć np. czujnik deszczu pod `input_boolean.nawadnianie_blokada_deszcz` przez prostą automatyzację.

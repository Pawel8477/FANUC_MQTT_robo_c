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
- [ ] Sprawdzić/uruchomić dodatek **Mosquitto broker** + integrację MQTT — *port 1883 jeszcze zamknięty (do instalacji)*
- [ ] Wgrać `packages/nawadnianie.yaml` + dashboard — *brak SSH/Samby, potrzebny File Editor / VS Code add-on lub włączenie Samby*
- [ ] Ustawić na płytce Dingtian broker = `192.168.8.50`, zarezerwować stałe IP w routerze — *płytka nieosiągalna pod `…8.100/1.100/7.1`, do zlokalizowania/podłączenia*
- [ ] Zweryfikować ruch MQTT i przetestować strefy

### Diagnostyka sieci (2026-06-30, z Maca `192.168.8.29`)
| Cel | Wynik |
|-----|-------|
| `192.168.8.50:8123` (panel HA) | ✅ `HTTP 200`, ~4 ms |
| `192.168.8.50:4357` (HAOS Observer) | ✅ otwarty → to **Home Assistant OS** z Supervisorem (add-ony dostępne) |
| `192.168.8.50:1883` (Mosquitto/MQTT) | ❌ zamknięty → broker jeszcze nie postawiony |
| `192.168.8.50:22` (SSH) / `:445` (Samba) | ❌ zamknięte → brak ścieżki sieciowej do `/config` |
| Płytka Dingtian | ❌ **nie ma jej w sieci** — skan całego `192.168.8.0/24` (11 żywych hostów) nie pokazał panelu płytki; `.49` = serwer Ubuntu (lighttpd), `.211` = panel innego urządzenia, `.1` = router. Płytka niezasilona lub niedołączona do WiFi → krok fizyczny |

## Następny krok
Panel HA potwierdzony. Kolejność:
1. **Mosquitto broker** — Settings → Add-ons → Add-on Store → *Mosquitto broker* → Install → Start (+ „Start on boot"). Załóż użytkownika MQTT (np. `ha`).
2. **Integracja MQTT** — Settings → Devices & Services → Add Integration → MQTT → broker `core-mosquitto` (lub `192.168.8.50`), port `1883`.
3. **Wgranie wsadu** — przez **File Editor** lub **Studio Code Server** add-on: utwórz `/config/packages/nawadnianie.yaml` (treść z tego repo) i w `configuration.yaml` dodaj `homeassistant: packages: !include_dir_named packages`. Restart.
4. **Dashboard** — wklej `lovelace_nawadnianie.yaml` w edytorze karty (tryb YAML).
5. **Płytka Dingtian** — zlokalizuj IP (skan sieci / panel routera), ustaw broker `192.168.8.50:1883`, zarezerwuj stałe IP po MAC.
6. **Test** — `mosquitto_sub -h 192.168.8.50 -u ha -P <hasło> -t '#' -v`, włącz „Strefę 1".

> Uwaga środowiskowa: ta sesja ma dostęp do sieci lokalnej (Mac `192.168.8.29`,
> HA odpowiada na `192.168.8.50`). Operacje wewnątrz HA (instalacja add-onów,
> integracja MQTT, zapis do `/config`) wymagają logowania do panelu HA — do zrobienia
> w UI albo przez automatyzację przeglądarki po zalogowaniu.

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
- [x] HA wstał, adres w sieci lokalnej: **`http://192.168.8.50:8123`** (do potwierdzenia)
- [ ] Potwierdzić, że panel HA się ładuje (`curl -I http://192.168.8.50:8123` z Maca)
- [ ] Sprawdzić/uruchomić dodatek **Mosquitto broker** + integrację MQTT
- [ ] Wgrać `packages/nawadnianie.yaml` + dashboard
- [ ] Ustawić na płytce Dingtian broker = `192.168.8.50`, zarezerwować stałe IP w routerze
- [ ] Zweryfikować ruch MQTT i przetestować strefy

## Następny krok
Z Maca (Terminal) potwierdź, że HA odpowiada:
```bash
curl -I http://192.168.8.50:8123
```
Potem: Mosquitto → wgranie package → konfiguracja MQTT na płytce → test stref.

> Uwaga środowiskowa: ta sesja Claude działa w chmurze (izolowany kontener Linux),
> więc nie ma dostępu do sieci lokalnej `192.168.x.x`. Testy sieciowe wykonujemy
> z Maca, albo odpalając Claude Code lokalnie w terminalu Maca.

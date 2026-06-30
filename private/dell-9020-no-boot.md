# Dell 9020 — "No bootable devices found" — diagnostyka

Komunikat = firmware nie znalazł nośnika z bootloaderem. Trzy możliwości:
(1) dysk nie jest wykrywany (kabel/zasilanie/martwy dysk),
(2) dysk wykryty, ale zmienił się tryb bootowania/SATA → OS „znika",
(3) bootloader/partycja EFI uszkodzona.

Klawisze Dell: **F2** = BIOS/Setup, **F12** = jednorazowe menu boot + diagnostyka.

---

## KROK 1 — Czy BIOS widzi dysk? (to rozstrzyga wszystko)
1. Włącz, naciskaj **F2** przy logo Dell.
2. Wejdź w **System Information / Drives / SATA** (zależnie od wersji BIOS).
3. Sprawdź, czy widać Twój dysk (HDD/SSD) z nazwą i pojemnością.

- **Dysk NIE jest widoczny** → problem sprzętowy, idź do KROK 2.
- **Dysk JEST widoczny** → problem z bootem/trybem, idź do KROK 3.

## KROK 2 — Dysk niewidoczny (sprzęt)
1. **Diagnostyka Dell (ePSA):** F12 → **Diagnostics**. Przejdzie test pamięci/dysku.
   - Zapisz ewentualny **kod błędu** (np. 2000-0142 = błąd dysku).
2. Odłącz zasilanie, otwórz obudowę i **przepnij kable** dysku:
   - SATA: kabel danych + kabel zasilania (spróbuj inny port SATA na płycie).
   - Jeśli NVMe M.2 — wyjmij i włóż ponownie w slot.
3. Jeśli po tym dalej niewidoczny → najpewniej **dysk padł**. To częsty powód.
   - Plan: i tak chcemy postawić Home Assistant — patrz sekcja „HA na tym Dellu".

## KROK 3 — Dysk widoczny, ale nie bootuje (BIOS/tryb)
Najczęstsze przyczyny po kolei:

1. **Boot Sequence / kolejność bootowania**
   - BIOS → **Boot Sequence** → upewnij się, że Twój dysk jest na liście i na górze.
   - Jeśli lista pusta / brak wpisu Windows Boot Manager → bootloader skasowany (pkt 4).

2. **Tryb boot: UEFI vs Legacy (bardzo częste!)**
   - BIOS → **Boot Mode** / Boot List Option.
   - System instalowany w UEFI nie zbootuje w Legacy i odwrotnie. Przełącz i sprawdź oba.

3. **SATA Operation: AHCI vs RAID**
   - BIOS → **SATA Operation**. Jeśli ktoś zmienił RAID↔AHCI, Windows nie wystartuje
     (BSOD/INACCESSIBLE_BOOT_DEVICE lub właśnie „no bootable device").
   - Ustaw z powrotem na to, w czym był instalowany OS (najczęściej **AHCI**).

4. **Secure Boot**
   - Jeśli walczysz, tymczasowo **wyłącz Secure Boot** (ułatwia też późniejszą instalację HA OS / Linuksa).

5. **F12 → menu boot** — zobacz, czy jest jakikolwiek wpis „Windows Boot Manager"
   lub dysk UEFI. Brak = uszkodzona partycja EFI (do naprawy z USB recovery).

---

## Skrót decyzyjny
- Test ePSA OK + dysk widoczny → to konfiguracja BIOS (KROK 3), nic nie padło.
- Test ePSA błąd / dysk niewidoczny po przepięciu kabli → dysk do wymiany.

---

## A jak już go diagnozujesz — postaw na nim Home Assistant
Ten Dell idealnie nadaje się na serwer HA (mocniejszy, bez umierającej karty SD):

**Opcja 1 — HA OS bare metal (najprościej, cała maszyna pod HA):**
1. Na innym kompie: Balena Etcher / RPi Imager → zapisz obraz
   **HAOS „Generic x86-64"** (.img) na pendrive.
   (haos_generic-x86-64-*.img.xz ze strony Home Assistant / GitHub releases)
2. W Dellu: F12 → boot z USB (UEFI), Secure Boot OFF.
3. Instalator sam wgra HAOS na dysk wewnętrzny. Po ~10 min wejdź na
   `http://homeassistant.local:8123`.

**Opcja 2 — Proxmox + HA jako VM** (jeśli chcesz też inne usługi na tym sprzęcie).
Bardziej elastyczne, ale więcej zachodu.

Po postawieniu HA wracamy do nawadniania:
- Mosquitto broker + integracja MQTT,
- wgrywamy `packages/nawadnianie.yaml` (+ dashboard),
- na płytce Dingtian ustawiamy broker na IP tego serwera (zarezerwuj stałe IP w routerze).
```bash
mosquitto_sub -h <IP_HA> -u ha -P <haslo> -t '#' -v   # weryfikacja
```
```
> Diagnozę dysku zrób PRZED instalacją HA — jeśli dysk jest martwy, instalacja i tak się nie uda.
```

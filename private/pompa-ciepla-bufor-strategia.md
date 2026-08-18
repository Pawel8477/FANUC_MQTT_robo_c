# Pompa ciepła + bufor 1000 l — strategia pracy i COP

Notatka decyzyjna do systemu grzewczego: **jak sterować pompą ciepła**, żeby nie
zmarnować COP, i **czy nabijać bufor w dzień** (odpowiedź: nie, poza CWU).

## Instalacja

| Element | Dane |
|---|---|
| Bufor | **1000 l** (wspólny dla wszystkich źródeł) |
| Źródło 1 | **Pompa ciepła 8 kW, monoblok** (nowa) |
| Źródło 2 | Kocioł gazowy |
| Źródło 3 | Kominek z płaszczem wodnym |
| Odbiorniki | Parter — podłogówka; piętro — **grzejniki**; łazienki — podłogówka |
| PV | **8 kWp, stare zasady (opust / net-metering 1:0,8)** |

---

## Wniosek nadrzędny

> **Nie nabijaj bufora pompą ciepła „na zapas".**
> Praca ciągła, modulowana, z krzywą grzewczą ustawioną najniżej jak dom zniesie.
> Bufor = sprzęgło hydrauliczne i zapas na rozmrażanie, **nie** magazyn energii.
> Wyjątek: **CWU — ładuj w południe**.

---

## Dlaczego nie nabijać (liczby)

1000 l to **1,16 kWh na każdy 1 K** różnicy temperatury. Każdy stopień podniesienia
temperatury zasilania kosztuje pompę ok. **2–3% COP**.

| Ładowanie bufora | Zmagazynowane | Koszt w COP |
|---|---|---|
| 35 → 40 °C | 5,8 kWh | ~12% |
| 35 → 45 °C | 11,6 kWh | ~25% |
| 35 → 50 °C | 17,4 kWh | ~35–40% |

Żeby zmagazynować jeden wieczór grzania, trzeba wejść w temperatury, przy których
COP leci z ~4,5 na ~3,0. Zysk z cieplejszego powietrza w południe to typowo
+2–4 K na zewnątrz, czyli **5–10% COP**. To się nie bilansuje.

### PV na opuście — sieć jest lepszym magazynem niż bufor

Stare zasady = net-metering **1:0,8 z rocznym okresem rozliczeniowym**. Nadwyżka
z lipca finansuje grzanie w styczniu, bez żadnej straty na COP.
**Bufor przesuwa energię o godziny. Sieć przesuwa ją o miesiące.**

Jeden kWh nadwyżki w marcowe południe:

| Wariant | Rachunek | Ciepło |
|---|---|---|
| Nabijam bufor (W45, COP ~3,2) − straty postojowe | 1,0 × 3,2 × 0,93 | **~3,0 kWh** |
| Oddaję do sieci, odbieram wieczorem (W35, COP ~3,6) | 0,8 × 3,6 | **~2,9 kWh** |

Remis — a wariant drugi jest prostszy, nie miesza bufora, nie powoduje taktowania
i nie zakłada, że wieczorem faktycznie będzie potrzeba tego ciepła.

> ⚠️ **To jest specyficzne dla opustu.** Gdyby instalacja przeszła na net-billing
> (autokonsumpcja warta ~2–3× więcej niż eksport), wariant pierwszy zaczyna wygrywać
> i strategię trzeba przeliczyć od nowa.

### Sezonowo i tak nie ma czego przesuwać

8 kWp ≈ 8000 kWh/rok, ale rozłożone odwrotnie do zapotrzebowania na ciepło:

| Miesiąc | Produkcja PV / dobę | Zużycie PC w mroźny dzień |
|---|---|---|
| Grudzień | ~3 kWh | 30–40 kWh |
| Styczeń | ~4,5 kWh | 30–40 kWh |
| Luty | ~11 kWh | 25–30 kWh |
| Marzec | ~19 kWh | 12–18 kWh |
| Październik | ~14 kWh | 8–12 kWh |

W grudniu i styczniu **nadwyżki nie ma w ogóle** — PV pokrywa ~10% tego, co zjada
pompa, razem z bytówką domu. Nadwyżka jest w marcu i październiku, gdy dom prawie
nie potrzebuje ciepła. Okno dla strategii „ładuję bufor z PV" to kilkanaście dni w roku.

---

## Gdzie PV realnie pomaga: CWU ✅

Do zasobnika CWU i tak trzeba wejść na 48–50 °C — ta wysoka temperatura kosztuje
niezależnie od pory doby. Więc rób to wtedy, gdy powietrze jest najcieplejsze:

- **Ładowanie CWU: okno ~10:00–15:00**
- **Antylegionella (grzałka): też w szczycie PV**, nie w nocy
- **Latem: CWU w całości z PV**

---

## Największy lewar na COP: grzejniki na piętrze

Pompa produkuje **jedną** temperaturę zasilania — najwyższą, jakiej wymaga
którykolwiek obieg. Zmieszanie podłogówki w dół nic nie daje: jeśli grzejniki chcą
50 °C, to pompa robi 50 °C dla całego domu, a parter dostaje to zmieszane.

**Każde 5 K w dół na temperaturze zasilania to ~12–15% na rachunku, przez cały sezon.**
To warte wielokrotnie więcej niż jakikolwiek harmonogram.

### Test do zrobienia przy najbliższym mrozie (~−5 °C)

1. Odkręć **na maksa wszystkie zawory termostatyczne na piętrze**.
2. Zejdź krzywą grzewczą do **40 °C** temperatury zasilania.
3. Daj domowi **2–3 doby** na ustabilizowanie (bezwładność podłogówki!).
4. Sprawdź, czy sypialnie trzymają temperaturę.

- **Trzymają** → masz to za darmo, zostaw niżej i spróbuj jeszcze −2 K.
- **Nie trzymają** → wymiana 2–3 najgorszych grzejników na większe albo na
  wentylatorowe (typu Jaga / konwektory z wentylatorem) wychodzi taniej niż
  różnica w rachunkach przez kilka sezonów.

> Grzejniki w domach jednorodzinnych są notorycznie przewymiarowane, a piętro ma
> z reguły mniejsze zapotrzebowanie niż parter (ciepło idzie do góry, mniej ścian
> zewnętrznych na m²). Szansa na sukces jest realna.

### Żadnego nocnego obniżenia ❌

Pompa ciepła ma najlepszą sprawność w pracy ciągłej modulowanej. Nocne obniżenie
i poranne dogrzewanie wymusza wyższe temperatury zasilania i kosztuje więcej, niż
oszczędza. Przy okazji: bez obniżeń naturalnie więcej pracy przypada na dzień,
gdy PV produkuje — bez żadnego wymuszania.

---

## Bufor 1000 l — jedyna rzecz, którą robi dobrze

Przy 8 kW monobloku minimalna moc modulacji to typowo 2,5–3 kW, a dom w październiku
potrzebuje może 2 kW. Bez bufora → **taktowanie**. I to jest sensowna rola tego
zbiornika: wydłużanie cykli i zapas na rozmrażanie. Nie magazynowanie.

### Hydraulika — na co uważać z kominkiem

Tu takie instalacje najczęściej się psują. Kominek wrzuca do bufora 60–70 °C;
jeśli pompa bierze z niego powrót, to albo stanie na zabezpieczeniu wysokiej
temperatury, albo będzie pracować z fatalnym COP.

- [ ] **Blokada pompy** przy wysokiej temperaturze bufora — kominek/kocioł grzeje → PC stoi.
      Pompa nie może „dogrzewać" po nich.
- [ ] **Bufor równolegle (sprzęgło), nie szeregowo** — PC musi móc zasilać obiegi
      bezpośrednio, gdy kominek nie pracuje. Przepuszczanie całego przepływu PC
      przez 1000 l miesza zbiornik i podnosi wymaganą temperaturę zasilania.
- [ ] **Króćce na właściwych wysokościach** — PC nisko (niskotemperaturowo),
      kominek i kocioł wyżej, żeby nie rozbijać uwarstwienia.
- [ ] Kocioł gazowy jako szczyt/backup przy dużym mrozie i przy awarii.

### Straty postojowe

1000 l to ~2–3 kWh/dobę strat. Jeśli bufor stoi w kotłowni **wewnątrz bryły
budynku**, zimą te straty częściowo wracają do domu. Latem — są stracone,
więc latem trzymaj bufor zimny (CWU osobno).

---

## Nastawy — checklista

- [ ] Krzywa grzewcza ustawiona najniżej, jak dom zniesie (test grzejników wyżej)
- [ ] **Brak** nocnego obniżenia, praca ciągła
- [ ] Bufor **nie** ładowany ponad to, czego wymaga aktualna krzywa
- [ ] CWU w oknie 10:00–15:00 + antylegionella w szczycie PV
- [ ] Blokada PC przy pracy kominka / kotła
- [ ] Zawory termostatyczne na piętrze otwarte (regulacja krzywą, nie dławieniem)
- [ ] Kocioł gazowy jako backup, nie jako równoległe źródło

---

## Stan integracji z Home Assistant

- [x] Serwer HA działa — `http://192.168.8.50:8123` (Dell 9020, HAOS)
- [x] Mosquitto broker + integracja MQTT
- [ ] **PV (8 kWp) — niewpięte w HA**
- [ ] **Pompa ciepła (8 kW monoblok) — niewpięta w HA**
- [ ] Czujniki temperatury bufora (góra / środek / dół) — brak
- [ ] Automatyzacja „CWU pod produkcję PV" — do zrobienia po wpięciu źródeł

### Co trzeba, żeby to ruszyć

1. **PV** — zależnie od falownika: większość (Fronius, SolarEdge, Huawei, Growatt,
   Sofar, Deye) ma integrację w HA albo przez Modbus TCP, albo przez chmurę
   producenta. Modbus lokalnie jest lepszy — bez zależności od internetu.
2. **Pompa ciepła** — marka decyduje. Część monobloków ma Modbus RTU/TCP albo
   gotową integrację (np. Daikin, Panasonic Aquarea przez CZ-TAW1, LG ThermaV,
   Viessmann, Stiebel/Tecalor przez ISG). Bez tego zostaje sterowanie
   „na styk" — przekaźnik na wejście EVU/SG-Ready.
3. **Termometry bufora** — 3× DS18B20 na ESP32/ESPHome do MQTT. Tanie i daje
   najwięcej wglądu (uwarstwienie, czy kominek nie miesza, czy PC nie taktuje).

> **SG-Ready jako plan minimum:** nawet bez pełnej integracji, jedno wyjście
> przekaźnikowe z HA na wejście SG-Ready pompy pozwala ją blokować, gdy pracuje
> kominek. To najważniejsza automatyzacja z całej listy.

---

## Do zweryfikowania / założenia

Liczby COP w tej notatce to wartości typowe dla monobloków powietrze-woda, nie
z karty konkretnego urządzenia. Po wpięciu pompy do HA warto zebrać realne dane
(pobór, ciepło, temperatury) i przeliczyć — zwłaszcza tabelę „nabijać / nie nabijać".

- [ ] Marka i model pompy ciepła (→ możliwości integracji, min. moc modulacji)
- [ ] Marka falownika PV (→ Modbus czy chmura)
- [ ] Czy istnieje osobny zasobnik CWU, czy CWU z wężownicy bufora
- [ ] Aktualna temperatura zasilania grzejników na piętrze przy mrozie
- [ ] Schemat podłączenia bufora (szeregowo czy równolegle) — do sprawdzenia w kotłowni

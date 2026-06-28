# Alvia — strona one-page

Statyczna, jednostronicowa strona firmy spedycyjno-transportowej **Alvia**,
zbudowana na podstawie dostarczonej treści.

## Zawartość

- `index.html` — struktura i treść strony (sekcje: Start, Usługi, O nas,
  Specjalizacje, Kierunki, Proces współpracy, Rozwiązania, Kontakt)
- `styles.css` — style (responsywne, paleta granat + akcent bursztynowy)
- `script.js` — menu mobilne, rok w stopce, obsługa formularza poglądowego

## Podgląd lokalny

Wystarczy otworzyć plik `index.html` w przeglądarce, albo uruchomić prosty serwer:

```bash
cd alvia-site
python3 -m http.server 8000
# następnie otwórz http://localhost:8000
```

## Uwagi

- Formularz kontaktowy jest **poglądowy** — nie wysyła wiadomości. Aby działał,
  podłącz `action` formularza do własnej obsługi poczty lub usługi formularzy
  (np. Formspree, własny endpoint).
- W treści źródłowej numeracja sekcji miała przeskok (po sekcji 6 następowała
  sekcja 8) oraz pojawiła się literówka w nazwie firmy („Alia") — w stronie
  ujednolicono nazwę na **Alvia** i uporządkowano kolejność sekcji.
- Dane kontaktowe (e-mail, telefon, NIP itp.) nie były podane w materiale
  źródłowym — należy je uzupełnić w sekcji „Kontakt" i w stopce.

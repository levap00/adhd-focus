# ADHD Focus — checklista rozwoju

Stan: 15.09.2026. Podstawa: lista potrzeb właściciela i kod aplikacji.
„Zrobione” oznacza funkcję obecną w kodzie; stan wdrożenia podajemy osobno.

## 1. Zrobione i wdrożone — naprawa formularza / Fala 0

[PR #7](https://github.com/levap00/adhd-focus/pull/7), gałąź `codex/fix-task-modal-mobile-20260915`.
Właściciel potwierdził, że po przełączeniu na tę wersję aplikacja działa.
PR pozostaje oddzielną zmianą do włączenia do `main`.

- [x] Dodawanie zadania i przejście z szybkiego wrzutu do szczegółów bez znikania okna.
- [x] Zamykanie formularza przywraca przewijanie strony.
- [x] Ciaśniejszy formularz telefonu: mniejsze odstępy, zwinięte szczegóły, osobna przewijana część i przyciski zapisu.
- [x] Gotowe podzadania chowają się po około 3 sekundach pod rozwijaną listą „Gotowe”.
- [x] Kolejność podzadań zmieniana strzałkami i zapisywana w istniejącym polu `position`.
- [x] Osobny wybór godzin i minut; zapis nadal jako liczba minut.
- [x] Nazwa zakładki „Zdrowie”. W środku nadal są leki; higiena i samopoczucie czekają na rozbudowę.
- [x] Podzadania o identycznych nazwach odhaczają się niezależnie.

Do oceny po zwykłym używaniu telefonu pozostają konkretne problemy z układem lub klawiaturą.
Długa lista podzadań może wymagać przewijania środka formularza. Stały dostęp do zapisu jest ważniejszy niż ściskanie dowolnie dużej listy na jednym ekranie.

## 2. Przygotowane teraz — przerwy w focusie

Gałąź `codex/focus-breaks-roadmap-20260915`, oparta na działającej poprawce formularza.
Ta paczka wymaga osobnego wdrożenia.

- [x] Przypomnienie domyślnie co 60 minut; wybór 50 / 60 / 90 minut albo wyłączenie.
- [x] „Jeszcze 15 min” odkłada przypomnienie bez zmiany domyślnej częstotliwości.
- [x] „Idę na przerwę” zatrzymuje timer zadania; „Wracam do zadania” wznawia pozostały czas.
- [x] Powrót do focusa zachowuje aktywne zadanie, timer i stan przerwy.
- [x] Timer uwzględnia upływ czasu po uśpieniu karty. Przypomnienia działają także po upływie szacowanego czasu zadania, do zakończenia sesji.
- [x] Częstotliwość zapamiętana w tej przeglądarce.
- [x] Błąd zapisu „Zrobione” pozostawia sesję, żeby można było ponowić zapis.
- [ ] Wdrożenie i sprawdzenie na własnym telefonie oraz komputerze.

Zakres: komunikat w otwartej aplikacji, również po przejściu do innego widoku podczas focusa.
Nie zasłania edytowanego formularza: oczekuje na jego zamknięcie.
Uśpiona karta pokaże zaległy komunikat po wznowieniu; zamknięta aplikacja nie wysyła tych przypomnień.
Odświeżenie strony kończy sesję, ale zachowuje ustawienie częstotliwości.
To jeszcze nie historia sesji ani powiadomienia push o przerwach.

## 3. Następne małe zmiany — bez przebudowy danych

| Kolejność | Funkcja | Stan i konkretny następny krok |
| --- | --- | --- |
| 1 | Wygodniejsze szczegóły zadania | Częściowo gotowe. Obecne chipy rozwijają szczegóły; następny krok to otwieranie konkretnego pola: data / moduł / priorytet / podzadania. Sprawdzić to na rzeczywistym sposobie dodawania zadania. |
| 2 | Liczba zadań obecnie po terminie | Logika wykrywania już istnieje. Dodać czytelny licznik z przejściem do listy. Ustalić zakres: moje zadania czy także udostępnione. |
| 3 | Średnie obecne opóźnienie otwartych zadań | Da się policzyć z aktualnych terminów. Najpierw ustalić, czy właśnie o tę miarę chodzi; nie jest to średnie spóźnienie zakończonych zadań. |

Nie dokładamy kolejnych pól do pełnego formularza, zanim nie sprawdzimy przepływu na małym ekranie.

## 4. Najpierw jedna decyzja, potem implementacja

| Temat | Proponowany minimalny zakres | Co ustalić przed kodem |
| --- | --- | --- |
| To samo zadanie w różne dni | Szablon + wybór kilku konkretnych dat; osobne zadanie na każdą datę | Czy zmiana szablonu dotyczy tylko przyszłych kopii? Propozycja: tak. Co kopiujemy: nazwę, moduł, czas, podzadania? |
| Data „od–do” / „od + czas” | Oddzielić okno wykonania od bloku z godziną startu i końca | Czy chodzi o „zrób między poniedziałkiem a środą”, czy „pracuję od 10:00 do 11:30”? To różne zachowania w kalendarzu. |
| „Też zrobiłem” | Jeden wpis: tytuł i automatyczna data; opcjonalna krótka notatka | Czy wpis ma być tylko osiągnięciem do podsumowania, czy także zadaniem? Propozycja: osobny krótki wpis, bez obowiązkowego modułu i planowania. |
| Podsumowanie tygodnia | Krótko: ukończone, ruszone/przerwane, dodatkowo zrobione | Zakres tygodnia i czy podsumowanie ma być tylko w aplikacji, czy również w powiadomieniu. |
| Zdrowie: higiena i nastrój | Dzienny widok: istniejące leki + proste rutyny + wpis samopoczucia | Jakie rutyny; jeden czy kilka wpisów nastroju dziennie. Harmonogramy leków zachowują własne zasady. |
| Jedzenie | W tym samym dniu: odhaczony posiłek + opcjonalne „co zjadłem” | Jakie posiłki i czy potrzebne są przypomnienia. Kalorie, makro i przepisy wymagają osobnej decyzji. |

Wybrane daty pasują do przykładu różnych dni w każdym tygodniu. Kwota „3 razy w tygodniu” pozostaje alternatywą, gdy dni nie mają znaczenia; nie trzeba budować obu modeli naraz.

## 5. Fundament pod uczciwe statystyki i podsumowania

- [ ] Historia zdarzeń zadania: utworzenie, zmiana terminu, ukończenie, ponowne otwarcie. Zapisywana na serwerze razem ze zmianą zadania.
- [ ] Zapamiętywanie terminu obowiązującego w chwili ukończenia. Dopiero na tej podstawie średnie spóźnienie ukończonych zadań i liczba przełożeń.
- [ ] Historia pracy w focusie: rozpoczęcie, przerwa, wznowienie, zakończenie; zasady dla kilku kart/urządzeń. Obecny timer nie jest jeszcze trwałym zapisem wykonanej pracy.
- [ ] Historia oczekiwanych dawek: kiedy lek był aktywny i jaki harmonogram obowiązywał danego dnia. Dopiero potem wiarygodne „opuszczone leki”.
- [ ] Krótkie wpisy „Też zrobiłem”, aby podsumowanie uwzględniało pracę poza planem.
- [ ] Podsumowanie tygodnia oparte na tych danych.

Dzisiejszy kod ma znaczniki ukończenia zadań w opisie, daty wykonania podzadań i dzienne odhaczenia leków. To pomaga w istniejącym tygodniu dopaminy, lecz nie odtwarza dawnych terminów ani zmian harmonogramu leków. Nie oznaczamy braku historii jako zera przełożeń lub pewnej pominiętej dawki.

## Proponowana kolejność kolejnych paczek

1. Przerwy w focusie — ta paczka.
2. Dopinanie szczegółów zadania oraz prosty licznik zaległości.
3. Historia zmian zadań, zanim rozbudujemy terminy i statystyki.
4. „Też zrobiłem”, historia focusa i krótkie podsumowanie tygodnia.
5. Szablon + wybrane daty; zakresy czasu po ustaleniu ich znaczenia.
6. Dzienny widok zdrowia, następnie prosty zapis posiłków.

Każda paczka dostaje własny PR i sprawdzenie konkretnego scenariusza. Zmieniamy kolejność, jeśli codzienne używanie ujawni pilniejszy problem.

## Sprawdzenie tej paczki

- Testy logiki: `node --test tests/test_task_ui.cjs tests/test_flow_ui.cjs`.
- Na urządzeniu: uruchom focus, wybierz częstotliwość, zrób przerwę, wróć do innego widoku i z powrotem. Timer ma zachować stan.
- Zaległe przypomnienie ma dać wybór przerwy lub odłożenia; po zakończeniu sesji ma zniknąć.
- Ponownie sprawdź dodawanie zadania, „Dodaj szczegóły” i przewijanie po zamknięciu formularza.

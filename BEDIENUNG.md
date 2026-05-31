# Hoftor-Steuerung — Bedienung & FAQ

**Für Claude-Instanzen:** Diese Datei ist die primäre Wissensquelle für Fragen zur Hoftor-Steuerung.  
**Technische Volldoku:** `CLAUDE.md` · **YAML-Quellcode:** `hoftor.yaml` (v0.28)  
**Web-Interface:** http://192.168.200.40 · **ESP-Name:** `hoftor`

---

## Das System in einem Satz

Ein ESP32 (Waveshare, PoE-versorgt) steuert ein zweiflügeliges BFT-Hoftor über 4 Befehlsrelais, liest 2 Endschalter-Eingänge (Tor offen / Tor zu) und meldet alles an Home Assistant. Alles ist auch über ein lokales Web-Interface bedienbar.

---

## Web-Interface — Gruppen-Übersicht

Das Interface unter http://192.168.200.40 ist in Gruppen gegliedert (Reihenfolge von oben nach unten):

| Gruppe | Was ist darin |
|---|---|
| **Störungs-Erkennung** | Alarmstatus + Schwellen-Einstellung (ganz oben, immer sichtbar) |
| **Ch1 — Tor auf** | Öffnen-Button, Dauerauf-Schalter, Auto-Schließ-Zeit + Countdown |
| **Ch2 — Tor zu** | Schließen-Button |
| **Ch3 — auf-stopp-zu** | Schritt-Button (Richtung wechseln) |
| **Ch4 — Fußgänger (Ped)** | Fußgänger-Button, Fußgänger-Dauerauf, Auto-Schließ-Zeit + Countdown |
| **LEDs (F7/F8)** | Status-LED blau + rot manuell schaltbar |
| **Eingänge (DI1-DI8)** | Live-Status aller digitalen Eingänge |
| **Test (Simulation)** | Test-Schalter für Bench-Test ohne angeschlossenes Tor |
| **Diagnose** | IP, Uptime, Chip-Temp, ESPHome-Version, API-Verbindung |

---

## Steuerkanäle — was macht welcher Button

### Ch1 — Tor öffnen (`pulse_open`)
- Schickt einen **1-Sekunden-Impuls** auf Relais r1 → BFT öffnet beide Flügel
- **Gesperrt** wenn Dauerauf aktiv (Button reagiert nicht)
- Der Auto-Close-Timer startet **nicht** beim Button — er startet wenn das Tor physisch die Endlage „offen" erreicht (DI1-Signal). Funktioniert daher auch bei Funk-Öffnung ohne ESP-Befehl.

### Ch1 — Dauerauf (Schalter)
- Hält Relais r1 **dauerhaft** — Tor bleibt offen bis Schalter manuell ausgeschaltet wird
- **LED rot** leuchtet solange Dauerauf aktiv
- Beim Ausschalten: 1 Sekunde Puffer, dann automatisch Close-Impuls
- **Blockiert** Fußgänger-Dauerauf (die beiden sperren sich gegenseitig)
- **DI3-Taster** (physisch, von außen): kann Dauerauf togglen — aber **nur wenn das Tor bereits offen ist** (Sicherheit: darf Tor nie selbst öffnen)

### Ch2 — Tor schließen (`pulse_close`)
- 1-Sekunden-Impuls auf Relais r2 → BFT schließt beide Flügel
- **Gesperrt** wenn Dauerauf oder Fußgänger-Dauerauf aktiv
- Stoppt laufende Auto-Close-Timer

### Ch3 — auf-stopp-zu (`pulse_step`)
- 1-Sekunden-Impuls auf Relais r3 → BFT wechselt Richtung
- Sequenz bei jedem Druck: öffnen → stoppen → schließen → öffnen → …
- **Gesperrt** wenn Dauerauf oder Fußgänger-Dauerauf aktiv
- Stoppt laufende Auto-Close-Timer

### Ch4 — Fußgänger (`pulse_ped`)
- 1-Sekunden-Impuls auf Relais r4 → BFT öffnet **nur einen Flügel** (Fußgänger-Stellung)
- BFT ist auf IC=6 „Timer Ped" konfiguriert: bei gehaltenem Impuls bleibt der Flügel offen
- **Gesperrt** wenn Dauerauf oder Fußgänger-Dauerauf aktiv
- Startet Auto-Close-Timer Ch4 wenn t > 0

### Ch4 — Fußgänger Dauerauf (Schalter)
- Hält Relais r4 dauerhaft → ein Flügel bleibt in Fußgänger-Position
- **Besonderheit:** Öffnen-Button Ch1 bleibt benutzbar! Tor fährt dann vollständig auf und kehrt danach zur Fußgänger-Position zurück (BFT IC=6-Feature)
- **LED rot** leuchtet solange aktiv
- Beim Ausschalten: 1 Sekunde Puffer, dann Close
- **Blockiert** Dauerauf

---

## Auto-Schließ-Funktion

### Ch1 Auto-Close
- Einstellbar: 0–600 Sekunden (`Ch1 — Auto-Schließ-Zeit`)
- **0 = deaktiviert** (Werkseinstellung)
- **Trigger:** DI1 wechselt 0→1 (Tor erreicht Endlage offen) — läuft also auch bei Funk-Öffnung
- **Nicht gestartet** wenn Dauerauf oder Fußgänger-Dauerauf aktiv
- **Gestoppt** bei: DI1 verlässt Endlage / Dauerauf EIN / Fußgänger-Dauerauf EIN / Ch2 Schließen / Ch3 Schritt
- **Countdown-Sensor** „Ch1 — Auto-Close Restzeit" zeigt verbleibende Sekunden (leer/unbekannt = kein Timer aktiv)

### Ch4 Auto-Close (Fußgänger)
- Einstellbar: 0–600 Sekunden (`Ch4 — Auto-Schließ-Zeit`)
- **Trigger:** sofort beim Drücken des Fußgänger-Buttons (nicht via DI)
- **Gestoppt** bei: Fußgänger-Dauerauf EIN / Ch2 / Ch3

---

## Status-LEDs

| LED | Physisch | Wann aktiv |
|---|---|---|
| **Blau (F7)** | Blaue Signalleuchte am Tor | Tor in Endlage „offen" (DI1=1) |
| **Rot (F8)** | Rote Signalleuchte am Tor | Dauerauf **oder** Fußgänger-Dauerauf aktiv |

- LEDs können auch manuell in HA/Web-UI überschrieben werden — werden beim nächsten automatischen Status-Trigger wieder korrekt gesetzt
- **5× rot blinken** = Verweigerungs-Signal: Taster von außen gedrückt aber Tor nicht offen

### Relais-Statustexte im Interface
- `🟢 angezogen` = Relais zieht gerade an (Impuls läuft)
- `🔴 aus` = Relais in Ruhe
- `🔵 leuchtet` / `⚫ aus` = LED-Zustand

---

## Digitale Eingänge (DI1–DI8)

| DI | Funktion |
|---|---|
| **DI1** | Endschalter „Tor offen" (BFT-Klemme 24/25 via Koppelrelais F3) |
| **DI2** | Endschalter „Tor zu" (BFT-Klemme 26/27 via Koppelrelais F4) |
| **DI3** | Externer Taster am Tor (von außen zugänglich) |
| DI4–DI8 | Reserve, nicht belegt |

**Wichtig:** DI1 und DI2 sind als kombinierte Template-Sensoren implementiert — sie reagieren auf physisches Signal **oder** Test-Schalter aus grp_test.

---

## Störungs-Erkennung

Wenn das Tor **weder** in Endlage offen (DI1=1) **noch** in Endlage zu (DI2=1) steht und **kein** Halte-Schalter aktiv ist, läuft ein Fehler-Timer.

### Eskalation 1 (Esk1)
- Schwelle einstellbar: `Störung — Esk1-Schwelle` (Standard: **180 Sekunden = 3 Minuten**, Bereich 30–1800 s)
- Sobald Schwelle überschritten: automatischer **Close-Impuls** + `Störung Eskalation 1 = EIN`
- Danach reset: Timer startet neu, Versuch wird gezählt

### Eskalation 2 (Esk2)
- Wenn nach `max Close-Versuche` (Standard: **3**, Bereich 1–10) das Tor immer noch in Zwischenposition ist
- `Störung Eskalation 2 = EIN` — keine weiteren automatischen Versuche mehr
- **HA sollte jetzt reagieren** (Push / Alexa / Sonos — der ESP benachrichtigt über HA)

### Automatische Quittierung
- Sobald DI1=1 **oder** DI2=1 → alle Esk-Flags werden zurückgesetzt, Counter = 0

### Pausiert bei
- `Dauerauf=EIN` oder `Fußgänger-Dauerauf=EIN` → Zwischenposition ist erwartet, kein Alarm

### Countdown-Sensor
- `Störung — Restzeit bis Esk1` zeigt Sekunden bis zum nächsten Close-Impuls
- Zeigt „unbekannt" wenn in Endlage oder Halten aktiv
- Zeigt 0 wenn Esk2 aktiv

---

## Halte-Logik — wichtige Regeln

1. **Dauerauf und Fußgänger-Dauerauf sperren sich gegenseitig** — nur eines kann aktiv sein. Versuch das andere einzuschalten wird abgelehnt (Schalter springt zurück).

2. **Beim Ausschalten eines Holds** gibt es **1 Sekunde Puffer** bevor der Close-Impuls gesendet wird. Wenn innerhalb dieser Sekunde ein Hold wieder eingeschaltet wird, wird der Close-Impuls abgebrochen.

3. **Beim Einschalten von Dauerauf:** laufende Auto-Close-Timer beider Kanäle werden gestoppt.

4. **Beim Einschalten von Fußgänger-Dauerauf:** laufende Auto-Close-Timer beider Kanäle werden gestoppt.

5. **Ch2 und Ch3** sind bei aktivem Halten gesperrt. **Ch1 Öffnen** ist nur bei aktivem Dauerauf gesperrt (nicht bei Fußgänger-Dauerauf — damit das BFT IC=6-Feature funktioniert).

---

## Test-Simulation (grp_test)

Für Bench-Test **ohne physisch angeschlossenes Tor** — simuliert Hardware-Signale:

| Element | Funktion |
|---|---|
| `Test: DI1 Tor offen` (Schalter) | Simuliert Endlage offen → LED blau, Auto-Close-Timer, Störungs-Timer reset |
| `Test: DI2 Tor zu` (Schalter) | Simuliert Endlage zu → Störungs-Timer reset, Esk-Quittierung |
| `Test: DI3 Taster` (Button) | Simuliert Taster-Druck → Dauerauf toggle wenn DI1=1, sonst 5× Blinken |
| `Test: LED rot 5× blinken` (Button) | Löst Verweigerungs-Blink-Muster manuell aus |

**Nach dem Test:** Schalter auf AUS setzen bevor das Tor angeschlossen wird. `restore_mode: ALWAYS_OFF` stellt sicher, dass sie nach ESP-Neustart immer aus sind.

---

## Close-Reaktions-Check (v0.30)

Wenn der Auto-Close-Timer abläuft und das Tor den Close-Befehl bekommt, aber **nicht reagiert** (DI1 bleibt 1 — Tor verlässt Endlage "offen" nicht), greift eine eigene Routine:

| Schritt | Was passiert |
|---|---|
| Auto-Close feuert `pulse_close` | `check_close_reaktion` startet gleichzeitig |
| Warte `stoer_esk1_sek` Sekunden | DI1 noch immer 1? → Tor hat nicht reagiert |
| Esk1 gesetzt + erneuter Close-Impuls | Retry-Schleife startet neu |
| Nach `max. Schließ-Versuche` | Esk2 gesetzt → HA benachrichtigt |
| DI1 fällt auf 0 (Tor bewegt sich) | Check wird gestoppt, Störungs-Interval übernimmt |

Reagiert das Tor auf einen Retry und DI1 fällt ab, aber das Tor bleibt dann in der Mitte stecken → **normaler Störungs-Interval** übernimmt (DI1=0, DI2=0 → Timer läuft → Esk1/Esk2).

Die Esk1/Esk2-Sensoren und Parameter (`stoer_esk1_sek`, `max. Schließ-Versuche`) werden von beiden Routinen gemeinsam genutzt.

---

## Häufige Fragen

**Warum schließt das Tor automatisch?**  
Auto-Close ist konfiguriert. Einstellung unter `Ch1 — Auto-Schließ-Zeit` auf 0 setzen um es zu deaktivieren.

**Warum reagiert der Schließen-Button nicht?**  
Dauerauf oder Fußgänger-Dauerauf ist aktiv. Diese sperren den Schließen-Button. Zuerst Halte-Schalter ausschalten.

**Warum reagiert der Dauerauf-Schalter nicht / springt zurück?**  
Fußgänger-Dauerauf ist aktiv (gegenseitige Sperre). Erst Fußgänger-Dauerauf ausschalten.

**Warum blinkt die rote LED 5×?**  
Der externe Taster (DI3) wurde gedrückt, aber das Tor war nicht in Endlage offen. Sicherheitssperre: der Außen-Taster darf das Tor nie selbst öffnen.

**Das Tor hängt in der Mitte — was passiert?**  
Nach der Esk1-Schwelle (Standard 3 Min) sendet der ESP automatisch einen Close-Befehl. Nach max. Versuchen (Standard 3) erscheint `Störung Eskalation 2` und HA sollte eine Benachrichtigung senden.

**Wie lange dauert der Auto-Close-Timer noch?**  
Sensor `Ch1 — Auto-Close Restzeit` zeigt die verbleibenden Sekunden. Zeigt „unbekannt" wenn kein Timer aktiv.

**Funktioniert Auto-Close auch bei Funk-Öffnung (Fernbedienung direkt ans BFT)?**  
Ja. Der Auto-Close-Trigger ist an DI1 (physischer Endschalter) geknüpft, nicht an den ESP-Button. Sobald das Tor die Endlage offen erreicht, startet der Timer — egal wie es geöffnet wurde.

**Was bedeuten die grünen/roten Symbole im Interface?**  
`🟢 angezogen` = Relais zieht gerade an (Schaltvorgang aktiv, Impuls läuft).  
`🔴 aus` = Relais in Ruhestellung.

**Was ist der Unterschied zwischen Ch1-Öffnen und Dauerauf?**  
Ch1-Öffnen sendet einen 1-Sekunden-Impuls → BFT öffnet und hält sich selbst (eigene TCA-Logik oder schließt nach BFT-TCA). Dauerauf hält das Öffnen-Relais dauerhaft → Tor bleibt garantiert offen bis der ESP-Schalter ausgeschaltet wird, unabhängig von BFT-interner TCA.

**Was ist Fußgänger-Modus?**  
Öffnet nur einen Torflügel (konfiguriert als BFT IC=6 „Timer Ped"). Sinnvoll wenn nur Personen, nicht Fahrzeuge, durchgehen sollen.

**Wie starte ich den ESP neu?**  
OTA-Update oder physischer Reset. Nach Neustart: alle Relais AUS, Test-Schalter AUS, Dauerauf AUS. Das Tor bleibt in seinem aktuellen physischen Zustand — BFT macht ohne Befehl nichts.

---

## Technische Kurzreferenz

| Parameter | Wert |
|---|---|
| IP-Adresse | 192.168.200.40 |
| Web-Interface Port | 80 (http) |
| API | ESPHome Native API (verschlüsselt) |
| Netzwerk | Ethernet (PoE), kein WLAN |
| Relais r1 | BFT 65 — Öffnen (Impuls) |
| Relais r2 | BFT 62 — Schließen (Impuls) |
| Relais r3 | BFT 64 — Schritt auf/stopp/zu |
| Relais r4 | BFT 61 — Fußgänger (IC=6) |
| Relais r5 | F7 Koppelrelais — LED blau |
| Relais r6 | F8 Koppelrelais — LED rot |
| DI1 | GPIO4 — Endschalter offen (BFT 24) |
| DI2 | GPIO5 — Endschalter zu (BFT 26) |
| DI3 | GPIO6 — Externer Taster |
| Impuls-Dauer | 1 Sekunde (alle Kanäle) |
| Auto-Close Default | 0 s (deaktiviert) |
| Esk1-Schwelle Default | 180 s (3 Minuten) |
| Max Close-Versuche Default | 3 |

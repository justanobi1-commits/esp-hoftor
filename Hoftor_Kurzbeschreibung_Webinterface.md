# Hoftor – Bedienung Web-Interface

Erreichbar im Browser unter **http://192.168.200.40**.
Die Bedienelemente sind in Gruppen sortiert. Jede Gruppe steuert einen Tor-Befehl
oder zeigt einen Status. Unten stehen die Funktionen in der Reihenfolge, wie man
sie im Alltag braucht.

> **Grundprinzip:** Jeder Befehl ist ein kurzer 1-Sekunden-Impuls an die Tor-Steuerung
> (BFT) – wie ein Tastendruck. Den tatsächlichen Tor-Zustand erkennt der ESP nur über
> die Endlagen-Melder (Tor offen / Tor zu), **nicht** über die Funk-Fernbedienung.

---

## 1. Tor auf (Gruppe „Ch1 — Tor auf")

| Element | Bedienung | Was passiert |
|---|---|---|
| **Öffnen** (Button) | Antippen | Tor fährt **beide Flügel** auf. Gesperrt, solange *Dauerauf* aktiv ist. |
| **Dauerauf** (Schalter) | Ein / Aus | **Ein:** Tor öffnet und bleibt offen, bis wieder ausgeschaltet. **Aus:** nach 1 Sekunde schließt das Tor automatisch. Kann nicht gleichzeitig mit *Fußgänger-Dauerauf* aktiv sein. |
| **Auto-Schließ-Zeit** (Zahl, 0–600 s) | Wert eingeben | Tor schließt selbsttätig nach dieser Zeit, **nachdem es die Endlage „offen" erreicht hat** (0 = Funktion aus). Wirkt auch bei Öffnung per Funk. |
| **Auto-Schließ-Restzeit** (Anzeige) | – | Countdown bis zum automatischen Schließen. |

---

## 2. Tor zu (Gruppe „Ch2 — Tor zu")

| Element | Bedienung | Was passiert |
|---|---|---|
| **Schließen** (Button) | Antippen | Tor fährt **beide Flügel** zu. Bricht laufende Auto-Schließ-Timer ab. Gesperrt, solange *Dauerauf* oder *Fußgänger-Dauerauf* aktiv ist. |

---

## 3. Auf-Stopp-Zu (Gruppe „Ch3 — auf-stopp-zu")

| Element | Bedienung | Was passiert |
|---|---|---|
| **auf-stopp-zu** (Button) | Antippen | Schritt-Befehl: jeder Druck wechselt **öffnen → stoppen → schließen → öffnen …** Gesperrt bei aktivem *Dauerauf* oder *Fußgänger-Dauerauf*. |

---

## 4. Fußgänger (Gruppe „Ch4 — Fußgänger (Ped)")

| Element | Bedienung | Was passiert |
|---|---|---|
| **Fußgänger** (Button) | Antippen | Öffnet **nur einen Flügel** (Fußgänger-Durchgang). Gesperrt bei aktivem Halten. |
| **Fußgänger Dauerauf** (Schalter) | Ein / Aus | **Ein:** ein Flügel bleibt dauerhaft offen. **Aus:** nach 1 Sekunde schließt das Tor. *Öffnen* (Ch1) bleibt möglich – das Tor fährt voll auf und kehrt danach in die Fußgänger-Stellung zurück. Nicht gleichzeitig mit *Dauerauf*. |
| **Auto-Schließ-Zeit** (Zahl, 0–600 s) | Wert eingeben | Schließt nach dieser Zeit nach einem Fußgänger-Befehl (0 = aus). |
| **Auto-Schließ-Restzeit** (Anzeige) | – | Countdown bis zum automatischen Schließen. |

> **Verriegelung:** *Dauerauf* und *Fußgänger-Dauerauf* sperren sich gegenseitig – es kann
> immer nur eines aktiv sein. Der Versuch, das zweite einzuschalten, wird abgelehnt und der
> Schalter springt zurück.

---

## 5. Status-LEDs (Gruppe „LEDs (F7 blau / F8 rot)")

| Element | Bedeutung |
|---|---|
| **LED blau** | Leuchtet, wenn das Tor in der Endlage **„offen"** steht. |
| **LED rot** | Leuchtet, wenn **Dauerauf** oder **Fußgänger-Dauerauf** aktiv ist. |

Die LEDs lassen sich von Hand schalten, werden aber beim nächsten Status-Wechsel
automatisch wieder korrekt gesetzt (der reale Zustand hat Vorrang).

---

## 6. Eingänge (Gruppe „Eingänge (DI1-DI8)") — nur Anzeige

| Eingang | Bedeutung |
|---|---|
| **DI1 — Tor offen** | Tor hat Endlage „offen" erreicht. |
| **DI2 — Tor zu** | Tor hat Endlage „zu" erreicht. |
| **DI3 — Taster** | Externer Taster am Tor (schaltet *Dauerauf* nur, wenn Tor bereits offen ist). |
| **DI4 – DI8** | Reserve. |

---

## 7. Störungs-Erkennung (Gruppe „Störungs-Erkennung", im Web-Interface ganz oben)

Erkennt, wenn das Tor **in einer Zwischenstellung hängen bleibt** (weder offen noch zu)
und versucht automatisch zu schließen.

| Element | Bedienung / Bedeutung |
|---|---|
| **Esk1-Schwelle** (Zahl, 30–1800 s) | Wartezeit in Zwischenstellung, bevor die erste Eskalation auslöst. Standard **180 s** (3 Min). |
| **max. Schließ-Versuche bis Esk2** (Zahl, 1–10) | Wie oft automatisch ein Schließ-Impuls versucht wird. Standard **3**. |
| **Störung Eskalation 1** (Anzeige) | 🚨 Tor hängt zu lange → ESP hat selbsttätig „Schließen" gesendet. |
| **Störung Eskalation 2** (Anzeige) | 🚨🚨 Auch nach allen Versuchen keine Endlage → **Home Assistant benachrichtigt** (Push/Alexa/Sonos). |
| **Restzeit bis Esk1** (Anzeige) | Countdown bis zum nächsten automatischen Schließ-Versuch. |

**Ablauf:** Zwischenstellung länger als die Schwelle → Schließ-Impuls + *Eskalation 1*
→ bleibt es ohne Erfolg, weitere Versuche bis zum Maximum → *Eskalation 2*.
Beide Meldungen erlöschen automatisch, sobald das Tor wieder „offen" oder „zu" meldet.
Während *Dauerauf* / *Fußgänger-Dauerauf* pausiert die Überwachung (Zwischenstellung ist hier gewollt).

---

## 8. Test / Simulation (Gruppe „Test (Simulation)")

Nur für den Prüfstand **ohne angeschlossenes Tor** – simuliert die Tor-Rückmeldungen.

| Element | Wirkung |
|---|---|
| **Test: DI1 Tor offen** (Schalter) | Simuliert „Tor offen" → LED blau, Auto-Schließen, Störungs-Reset wie echt. |
| **Test: DI2 Tor zu** (Schalter) | Simuliert „Tor zu" → Störungs-Reset wie echt. |
| **Test: DI3 Taster** (Button) | Simuliert den externen Taster. |
| **Test: LED rot 5× blinken** (Button) | Prüft das Verweigerungs-Blinkmuster. |

> Vor dem Anschluss an das echte Tor alle Test-Schalter auf **Aus** stellen (passiert auch automatisch nach Neustart).

---

## 9. Diagnose (Gruppe „Diagnose")

| Element | Bedeutung |
|---|---|
| **Verbindung (API)** | Ein = Home Assistant verbunden. |
| **Uptime** | Laufzeit seit letztem Neustart. |
| **Chip-Temperatur** | Temperatur des ESP. |
| **IP- / MAC-Adresse** | Netzwerk-Daten. |
| **ESPHome-Version** | Firmware-Stand. |

---

### Sicherheits-Hinweise
- Der **externe Taster (DI3)** kann das Tor **nie selbst öffnen** – er schaltet *Dauerauf*
  nur um, wenn das Tor bereits offen ist. Sonst blinkt die rote LED 5× (Verweigerung).
- Der **Web-Schalter „Dauerauf"** hat aktuell keine solche Sperre (Passwortschutz geplant).
- Nach einem Neustart sind **alle Relais aus**; das Tor verbleibt in seiner aktuellen
  physischen Stellung – die Steuerung fährt nichts von selbst.

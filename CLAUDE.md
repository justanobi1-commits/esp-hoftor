# Hoftor-Steuerung — Umbau Shelly → ESP

**Version:** 1.2
**Stand:** 27-05-2026
**Status:** Hardware-Auswahl & BOM final, Hauptbestellungen versendet, Layout fix, PDF-Schaltplan v2 erstellt. Cross-References (v1.2) ergänzt.

## Cross-References (HA-Doku)

Dieses ESP-Projekt hat (geplante) HA-Berührungspunkte. Sobald in Betrieb, **auch aktualisieren**:
- `homeassistant/dachgeschoss/automationen_uebersicht.md` — geplant: Cover-Entity, Dauerauf-Logik, LED-Blink-Logik (HT9)
- `homeassistant/dachgeschoss/helfer_uebersicht.md` — geplant: ggf. Status-Helfer
- `homeassistant/dachgeschoss/integrationen_uebersicht.md` — geplant: ESPHome Waveshare ESP32-S3-POE-ETH
- `homeassistant/dachgeschoss/geraete_uebersicht.md` — geplant: Hardware-Eintrag Hoftor-Steuerung
- `homeassistant/dachgeschoss/dashboards_uebersicht.md` — ggf. Steuer-Karte
- Memory `project_hoftor_esp.md` — Pointer-Datei

## Bestellstatus (26-05-2026)

| Bestellung | Inhalt | Status |
|---|---|---|
| **automation24 #2026-3047210** | Alles Phoenix (Klemmen, PTFIX, RIF-0, Adapter) + FIBOX MCE65 36M Verteiler | **versendet 26-05-2026** ✅ |
| **Amazon (priz24)** | 2× Phoenix PT 2,5-TWIN (Art. **3209549**, je 9,06 €) | **versendet 26-05-2026** ✅ |
| **Waveshare ESP32-S3-POE-ETH-8DI-8RO** | 1× Steuerung | Eintreffen 27-05-2026 ✅ |
| **ETUKER Anhängerkabel 13×0,5** (5 m, 24,46 €) | Tor-↔-Verteiler-Strecke + Innenverdrahtung mit durchgehender Farbe | bestellt, Eintreffen Freitag 29-05-2026 ✅ |
| **Glassicherung 2 A T 5×20** | 2–3 Stk | im Bestand vorhanden |
| **Aderendhülsen 0,5 mm²** | bei Bedarf | im Bestand vorhanden |
| **H07V-K 0,5 mm²** | rot/blau/schwarz/grau/grün/gelb je 15 m | im Bestand vorhanden |

---

## 1. Projektziel

Ablösung von **3× Shelly Uni Plus** durch **1× Waveshare ESP32-S3-POE-ETH-8DI-8RO** zur Steuerung einer **BFT Hoftor-Anlage Thalia BT A80/A160 mit EBD-Erweiterungskarte**.

Gründe für Umbau:
- Schlechter WLAN-Empfang der Shellys am Standort → PoE-Anbindung gewünscht
- Konsolidierung auf 1 zentrales Gerät statt 3 verteilte
- Bessere Diagnose-Möglichkeiten (LEDs an Koppelrelais zeigen jeden Befehlszustand)

## 2. BFT Hoftor-Anlage — Steuerung

**Modell:** BFT Thalia BT A80 oder A160 (gleiche Klemmenbelegung)
**Zusatzkarte:** **BFT EBD** (Art. 2614326) — bringt 2 weitere Befehlseingänge + 4 nicht-programmierbare Sicherheitseingänge

**Anleitung:** `C:\Users\obero\Downloads\Thalia-BT-A80-BT-A160-19.05.2025.pdf`

### Konfiguration BFT (im Display abgelesen, bestätigt)

| BFT-Klemme | Logik | Funktion |
|---|---|---|
| 60 | – | COM IC Hauptplatine |
| **61** | **IC1 = 2 (Open)** | Dauerauf (dauerhaft halten) |
| **62** | **IC2 = 3 (Close)** | schließen (Impuls) |
| 63 | – | COM IC EBD |
| **64** | **IC3 = 0 (Start E)** | Schritt (auf/stopp/zu Impuls) |
| **65** | **IC4 = 2 (Open)** | öffnen (Impuls) |
| **24/25** | AUX = ? (Zustand offenes Tor) | Status Tor offen (potentialfrei) |
| **26/27** | AUX = ? (Status Tor geschlossen) | Status Tor zu (potentialfrei) |

**Open-Redundanz**: IC1 und IC4 sind beide auf "Open" konfiguriert. **Bewusst gewählt** — visuelle Diagnose über LED am jeweiligen Koppelrelais zeigt, ob aktuell "öffnen Impuls" (F1) oder "Dauerauf" (F6) aktiv ist.

### AUX-Logik-Optionen Thalia BT A80 (für spätere Reference)

| Logik | Funktion |
|---|---|
| 1 | SCA Kontrollleuchte Tor offen (blinkt bei Schließung) |
| 6 | Blinkleuchte |
| 13 | **STATUS TOR GESCHLOSSEN** — Kontakt zu wenn Tor geschlossen |
| 16 | **ZUSTAND OFFENES TOR** — Kontakt zu wenn Tor offen |

### IC-Logik-Optionen Thalia BT A80

| Logik | Funktion |
|---|---|
| 0 | Start E (Schritt extern) — klassische auf/stopp/zu |
| 1 | Start I (Schritt intern, für Ampelsteuerung) |
| 2 | Open — Impuls öffnet (Auto-Close nach TCA); dauerhaft = Tor bleibt offen |
| 3 | Close — Impuls schließt |
| 4 | Ped — partielle Fußgängeröffnung |
| 5 | Timer — wie Open, aber Stromausfall-Sicherheit |
| 6 | Timer Ped |

## 3. Aktueller Aufbau (Bestand)

**3× Shelly Uni Plus** in Unterverteilung des Tors:

- **Shelly 1**: K1 = Schritt (Impuls), K2 = Dauerauf (dauer), IN0 = Taster
- **Shelly 2**: K1 = LED rot (Dauerauf-Anzeige + Blink), K2 = LED blau (Tor offen), IN1 = Status offen, IN2 = Status zu
- **Shelly 3**: K1 = öffnen (Impuls), K2 = schließen (Impuls)

**8× Finder 34.51.7.024.0010** mit Sockel **93.01.7.024** als galvanische Trennung zwischen Shelly-Seite und Tor-Seite. Diese werden 1:1 durch Phoenix RIF-0 ersetzt.

## 4. Neuaufbau — Hardware

### Verteiler-Gehäuse
**FIBOX MCE65 36M** — 3×12 TE Hutschienenverteiler, IP65, geeignet für Schuppen.

### Stromversorgung-Strang (230V → 24V DC)
- **B16 LS-Automat** (in Hauptverteilung) — bestehend
- **230V Zuleitung** → 2. Verteilung am Schuppen
- **ABB Ausschalter** (1 TE) — Hand-Trennstelle, bestehend
- **DEWIN 24V/1,5A/36W Hutschienen-Netzteil** (~2 TE) — bestehend
- **Hutschienen-Glassicherungshalter** (1 TE) + **Glassicherung 2A T 5×20** — bestehend; Reserve-Sicherungen 2× im Bestand
- → liefert 24 V DC SELV

### Potentialverteilung 24V
- **Phoenix PTFIX 6/12X2,5 RD** (Art. **3273356**) — +24V, 12 Abgänge à 2,5 mm²
- **Phoenix PTFIX 6/12X2,5 BU** (Art. **3273354**) — GND, 12 Abgänge
- **2× Phoenix PTFIX-NS35** (Art. **3274054**) — Tragschienen-Adapter (1 je PTFIX)

### Koppelrelais (Ersatz der 8 Finder)
- **8× Phoenix RIF-0-RPT-24DC/21** (Art. **2903370**) — All-in-One Koppelrelais, 24V DC Spule, Pickup ~17V, 6,2 mm Push-in, 1 Wechsler 6A

### Reihenklemmen (Block 1 — externe Verbindung zur BFT)
- **8× Phoenix PT 2,5** (Art. **3209510**) — Push-in Durchgangsklemme grau
- **2× Phoenix PT 2,5-TWIN** (Art. **3209549**, von Amazon) — 1 Eingang + 2 Ausgänge, für Klemmen #1 (BFT 60) und #4 (BFT 63) wo 2 COMs gebraucht werden
- **1× Phoenix D-ST 2,5** (Art. **3030417**) — Endplatte (vom Shop als Zubehör zur PT 2,5 bestätigt)
- **1× Phoenix FBS 2-5** (Art. **3030161**) — Steckbrücke 2-polig, brückt GND-Klemmen 9↔10
- **2× Phoenix CLIPFIX 35** (Art. **3022218**) — Endhalter
- **1× Phoenix ZB 5 Zahlen 1-10** (Art. **1050025**) — Beschriftungsstreifen vorgedruckt

### ESP-Steuerung
- **Waveshare ESP32-S3-POE-ETH-8DI-8RO** — 10 TE, PoE-versorgt, 8 Relais + 8 isolierte DI
- Versorgung: **PoE primär** (Cat-Kabel zum PoE-Switch); 24V VIN als Backup-Option

### Kabel
- **Anhängerkabel 13×0,5 mm²** (5 m, Amazon) — Strecke Tor ↔ Verteiler-Klemmen, < 1 m in trockenem Schuppen
- 10 Adern verwendet, 3 Reserve
- **Konzept**: Mantel nur im Leerrohr (< 1 m); im Verteiler wird der Restmantel entfernt und die Einzeladern werden bis zu den Phoenix RIF-0 Spulen/Kontakten durchgeführt
- → **Durchgehende Farbcodierung** vom BFT bis zur Spule, eine Farbe = eine Funktion
- Aderfarben-Zuordnung wird bei Eintreffen festgelegt und hier ergänzt

### Bestehendes Material (nicht neu zu kaufen)
- Aderendhülsen 0,5 mm² (Standard-Sortiment)
- H07V-K 0,5 mm² in **rot, blau, schwarz, grau, gelb, grün** (je 15 m)
- H07V-K 1 mm² in schwarz
- Twin-Aderendhülsen 2×0,5 mm² (von Amazon, falls TWIN-Klemmen nicht passen)

## 5. Klemmenbelegung (FINAL)

### J-Y(St)Y / Ölflex Tor ↔ Verteiler — 10 Adern

| Ader / WAGO# | BFT-Klemme | Funktion |
|---|---|---|
| 1 | 60 | COM Hauptplatine |
| 2 | 61 | Open (Dauerauf-Eingang) |
| 3 | 62 | Close |
| 4 | 63 | COM EBD |
| 5 | 64 | Start E (Schritt) |
| 6 | 65 | Open (Impuls) |
| 7 | 24 | Status Tor offen — Signal |
| 8 | 26 | Status Tor zu — Signal |
| 9 | 25 | Status Tor offen — GND |
| 10 | 27 | Status Tor zu — GND |

**Hinweis:** Klemmen 8 und 9 wurden **umsortiert** gegenüber natürlicher BFT-Reihenfolge, damit GNDs (9 und 10) adjacent sind → FBS 2-5 Brücker funktioniert.

### Phoenix Reihenklemmen-Anordnung (10 Stück)

```
[CF] [1-TWIN] [2-PT] [3-PT] [4-TWIN] [5-PT] [6-PT] [7-PT] [8-PT] [9-PT] [10-PT] [D]
       ↑                       ↑                                    └─FBS 2-5─┘
       BFT 60                  BFT 63                               GND-Brücke
       → F2-14 + F6-14         → F1-14 + F5-14
```

- TWIN-Klemmen an Position #1 und #4 (jeweils 1 Eingang + 2 Ausgänge)
- Normale PT 2,5 an Positionen #2, 3, 5, 6, 7, 8, 9, 10
- D-ST 2,5 Endplatte rechts; CLIPFIX 35 (CF) links + rechts als Endhalter
- FBS 2-5 zwischen 9 und 10 (GND-Brücke)
- ZB 5 Beschriftung mit Nummern 1-10

### ESP-Pin → Phoenix RIF-0 → Tor-Funktion

| ESP-Pin | Relais | Funktion | Schaltet Kontakt zwischen (Phoenix-Anschluss) |
|---|---|---|---|
| Relais R1 | **F1** | Befehl öffnen (Impuls) | Klemme 6 (BFT 65) ↔ Klemme 4 (BFT 63 COM-EBD) — über RIF-0 11→14 |
| Relais R2 | **F2** | Befehl schließen (Impuls) | Klemme 3 (BFT 62) ↔ Klemme 1 (BFT 60 COM-Haupt) |
| Relais R3 | **F5** | Befehl Schritt (Impuls) | Klemme 5 (BFT 64) ↔ Klemme 4 (BFT 63 COM-EBD) |
| Relais R4 | **F6** | Befehl Dauerauf (dauerhaft) | Klemme 2 (BFT 61) ↔ Klemme 1 (BFT 60 COM-Haupt) |
| Relais R5 | **F7** | LED blau ein (Tor offen) | +24V ↔ LED blau (Anode); Kathode → GND mit 1kΩ Vorwiderstand |
| Relais R6 | **F8** | LED rot ein (Dauerauf aktiv) | +24V ↔ LED rot (Anode); Kathode → GND mit 1kΩ Vorwiderstand |
| Eingang DI1 | **F3** | Status Tor offen lesen | F3 Kontakt 11(GND)→14(DI1) wenn BFT 24-25 schließt |
| Eingang DI2 | **F4** | Status Tor geschlossen lesen | F4 Kontakt 11(GND)→14(DI2) wenn BFT 26-27 schließt |
| Eingang DI3 | – | Taster Dauerauf-Auslöser | externer Taster gegen +24V |
| R7, R8 | – | Reserve |
| DI4–DI8 | – | Reserve |

### Phoenix RIF-0 Anschluss-Übersicht (alle 8)

**Befehls-Relais F1, F2, F5, F6** (ESP-getrieben, schalten Tor-Befehl):
- A1 → PTFIX +24V (alle gemeinsam)
- A2 → ESP-Relais R1/R2/R3/R4 (individuell)
- 11/14 → bridges zur BFT-Befehlsklemme + COM (siehe Tabelle oben)

**LED-Relais F7, F8** (ESP-getrieben, schalten LED-Strom):
- A1 → PTFIX +24V
- A2 → ESP-Relais R5/R6
- 11 → PTFIX +24V (zum Schalten)
- 14 → LED-Anode (mit 1kΩ Vorwiderstand zu GND)

**Status-Relais F3, F4** (BFT-getrieben, melden Status an ESP):
- A1 → PTFIX +24V
- A2 → Reihenklemme 7 bzw. 8 (BFT-Statussignal)
- 11 → PTFIX GND
- 14 → ESP DI1 bzw. DI2

## 6. Layout im Verteiler (3×12 TE FIBOX MCE65 36M)

```
Reihe 1 — Stromversorgung (8 TE belegt, 4 TE Reserve)
┌─────┬─────────┬─────┬───────────┬───────────┬─────────────────────┐
│ ABB │  DEWIN  │ Si. │ PTFIX rot │ PTFIX blau│      Reserve        │
│ Aus │  PSU    │ 2A  │   +24 V   │    GND    │                     │
│ 1TE │  2 TE   │ 1TE │   2 TE    │    2 TE   │       4 TE          │
└─────┴─────────┴─────┴───────────┴───────────┴─────────────────────┘

Reihe 2 — Schaltlogik (6 TE belegt, 6 TE Reserve)
┌──────────────┬──────────────┬─────────────────────────────────────┐
│  8× RIF-0    │ 10× PT 2,5   │              Reserve                │
│ Koppelrelais │ Reihenklem.  │                                     │
│    3 TE      │     3 TE     │              6 TE                   │
└──────────────┴──────────────┴─────────────────────────────────────┘

Reihe 3 — ESP-Steuerung (10 TE belegt, 2 TE Reserve)
┌──────────────────────────────────────────────────────┬───────────┐
│        Waveshare ESP32-S3-POE-ETH-8DI-8RO            │  Reserve  │
│              10 TE                                   │    2 TE   │
└──────────────────────────────────────────────────────┴───────────┘
```

**Anordnung-Logik:**
- **230 V** ganz oben (Reihe 1) — klare Trennung Hoch-/Niederspannung
- **24 V Schaltlogik** in der Mitte (Reihe 2)
- **ESP-Steuerung** unten (Reihe 3) — bei Wartung gut erreichbar
- Tor-Kabel-Einführung von unten, kommt nahe Klemmenleiste in Reihe 2 rein
- PoE-Cat-Kabel zum ESP RJ45 in Reihe 3

**Gesamt:** 24 TE belegt, **12 TE Reserve** → Erweiterungs-Reserve für Klingel, Lichtschranke, weitere Sensoren etc.

## 7. Verdrahtungs-Konvention

| Pfad | Querschnitt | Aderfarbe |
|---|---|---|
| 230 V → PSU | 1,5 mm² | L: schwarz, N: blau, PE: gn-ge |
| PSU → Sicherung → PTFIX | 0,5 mm² | rot (+24V), blau (GND) |
| PTFIX → RIF-0 Spule A1 (+24V) | 0,5 mm² | rot |
| RIF-0 → PTFIX GND | 0,5 mm² | blau |
| ESP-Relais → RIF-0 A2 | 0,5 mm² | schwarz |
| RIF-0 Kontakte → Reihenklemmen | 0,5 mm² | grün/grau |
| Reihenklemmen → Ölflex → Tor | 0,5 mm² (Ölflex 12G0,5) | nach Adernummer |

PTFIX Klemmbereich Eingang: 0,2–6 mm² → 0,5 mm² passt.
PT 2,5 Klemmbereich: 0,2–4 mm² eindrähtig → 0,5 mm² passt.
RIF-0 Push-in: 0,5 mm² mit Aderendhülse einschiebbar.

## 8. Open Points / Nächste Schritte

### Bestellungen
- [x] **automation24 #2026-3047210** — versendet 26-05-2026 (Phoenix-Komplettpaket + Verteiler)
- [x] **Amazon 2× PT 2,5-TWIN** — versendet 26-05-2026
- [x] **Waveshare ESP32-S3-POE-ETH-8DI-8RO** — Eintreffen 27-05-2026 ✅
- [x] **ETUKER Anhängerkabel 13×0,5** (5 m, 24,46 €) — Eintreffen Freitag 29-05-2026 ✅

### Aufbau (nach Wareneingang)
- [ ] Hardware im FIBOX MCE65 36M nach Layout montieren
- [ ] 24 V-Seite verdrahten (PSU → Sicherung → PTFIX → Verbraucher)
- [ ] 8× Phoenix RIF-0 verdrahten nach PDF v2 Schaltplan
- [ ] Reihenklemmen montieren (8× PT 2,5 + 2× PT 2,5-TWIN an Position #1 und #4)
- [ ] FBS 2-5 Brücke zwischen Klemme 9 und 10 (GND)
- [ ] Aderfarben-Zuordnung festlegen sobald Anhängerkabel da
- [ ] Tor-Kabel im Leerrohr verlegen, Adern im Verteiler entmantelt zu RIF-0 führen

### Test & Migration
- [ ] **Parallel-Test**: Neues System aufbauen, mit temporärer 24V-Quelle testen, ohne Bestand zu stören
- [ ] Migration: Bestand abklemmen, neues System einklemmen

### Software
- [ ] **ESPHome YAML** für Waveshare schreiben
  - 6 switch (Relais R1-R6)
  - 3 binary_sensor (DI1-DI3)
  - HA-Integration (cover.gate, sensor.gate_open, sensor.gate_closed, button.dauerauf)
- [ ] **Home Assistant Automationen**
  - Dauerauf-Logik: Taster gedrückt + Tor offen → R4 dauerhaft halten bis erneut gedrückt oder Tor schließen-Befehl
  - LED-Blink-Logik: Wenn Dauerauf-Taster gedrückt aber Tor nicht offen → R6 (LED rot) 5× blinken
  - Cover-Entity mit Position aus DI1/DI2 ableiten

## 9. Wichtige Entscheidungen & Erkenntnisse

### 6V-Messung an F3/F4 (geklärt)
Im **inaktiven Zustand** der BFT-Statusklemme (Tor in anderem Zustand) fließt durch die Spule eine **Streu-/Leckspannung von ~6V** (Multimeter-Anzeige). Im **aktiven Zustand** (Statuskontakt geschlossen) liegen die vollen 24V vom PSU an. **Kein Problem für Phoenix RIF-0** (Pickup ~17V, gleiche Charakteristik wie bestehende Finder 34.51).

### Stromart-Klärung (alles DC)
- BFT IC-Eingänge (60–65): erwartet Kontaktbrücke gegen COM, BFT-intern 24V DC
- BFT Status-Ausgänge 24/25, 26/27: potentialfrei (FREIER KONTAKT N.O.) — Anwender speist eigene DC ein
- Alle Stromkreise in Verteiler: 24V DC
- AUX 1 (Klemme 20-21, gespeister 24V Kontakt) wird **nicht verwendet** im Setup → AC/DC-Ambiguität dort irrelevant

### Twin-Klemmen-Lösung
Klemmen #1 (BFT 60) und #4 (BFT 63) brauchen jeweils 2 Abgänge nach unten (zu 2 Relais). Lösung: **PT 2,5-TWIN** (3-polig) statt normale PT 2,5. Twin-AEH als Alternative wäre auch gegangen.

### Dauerauf-Logik in HA vs. eigenes Relais
User-Entscheidung: **eigenes Relais F6** behalten (statt nur in HA via "Open-Relais R1 dauerhaft halten"). Gründe: visuelle Diagnose, Klarheit, Trennung der Anwendungsfälle "öffnen Impuls" vs "Dauerauf gehalten".

### Absicherung 24V-Seite
Trotz PSU mit Strombegrenzung wird eine **Glassicherung 2A T** (träge) im Hutschienen-Sicherungshalter zwischen PSU+ und PTFIX rot eingesetzt. Optional aber empfohlen für Service-Trennpunkt und Schutz bei Verdrahtungsfehlern.

## 10. Dateien & Referenzen

| Datei | Speicherort |
|---|---|
| Diese Doku | `C:\Users\obero\OneDrive\claude\.claude\esp\hoftor\CLAUDE.md` |
| Aderfarben-Template | `C:\Users\obero\OneDrive\claude\.claude\esp\hoftor\aderfarben_template.md` |
| PDF Schaltplan v2 | `C:\Users\obero\OneDrive\claude\.claude\esp\hoftor\Schaltplan_Hoftor_v2_KlemmenRelais.pdf` |
| Python Generator v2 | `C:\Users\obero\OneDrive\claude\.claude\esp\hoftor\make_schaltplan_v2.py` |
| PDF Schaltplan v1 (Übersicht) | `C:\Users\obero\OneDrive\claude\.claude\esp\hoftor\Schaltplan_Hoftor_v1.pdf` |
| Python Generator v1 | `C:\Users\obero\OneDrive\claude\.claude\esp\hoftor\make_schaltplan.py` |
| BFT Thalia BT A80 Anleitung | `C:\Users\obero\Downloads\Thalia-BT-A80-BT-A160-19.05.2025.pdf` |

### Shops/Bezugsquellen
- **automation24.de** — Phoenix-Klemmen, Koppelrelais, PTFIX, FIBOX-Verteiler (alles 1× verfügbar, keine Großpackungen)
- **Amazon** — PT 2,5-TWIN 3-polig (Phoenix-Äquivalent oder Drittanbieter)
- **Waveshare-Shop / Amazon / AliExpress** — ESP32-S3-POE-ETH-8DI-8RO
- **Conrad/Reichelt/Baumarkt** — Glassicherungen 2A T 5×20

### Wichtige Artikelnummern

```
automation24 #2026-3047210 (versendet 26-05-2026):
Klemmenleiste:
  10× Phoenix 3209510   PT 2,5 (Push-in 2,5 mm² grau)
                        — davon werden im Aufbau nur 8 verwendet
                        — 2 Stück als Reserve verfügbar
                        (Klemmen #1 und #4 werden durch Amazon-TWIN ersetzt)
   1× Phoenix 3030417   D-ST 2,5 (Endplatte, vom Shop als kompatibel zu PT 2,5 bestätigt)
   1× Phoenix 3030161   FBS 2-5 (Steckbrücke 2-pol., GND-Brücke zwischen Klemme 9+10)
   2× Phoenix 3022218   CLIPFIX 35 (Endhalter)
   1× Phoenix 1050025   ZB 5 Zahlen 1-10 (Beschriftung vorgedruckt)

Potentialverteilung:
   1× Phoenix 3273356   PTFIX 6/12X2,5 RD (+24V rot)
   1× Phoenix 3273354   PTFIX 6/12X2,5 BU (GND blau)
   2× Phoenix 3274054   PTFIX-NS35 (Tragschienen-Adapter, je 1 pro PTFIX)

Koppelrelais:
   8× Phoenix 2903370   RIF-0-RPT-24DC/21 (Push-in, 24V DC, 6A)

Verteiler:
   1× FIBOX 7350006     MCE65 36M (3×12 TE IP65)

Gesamtsumme: 189,45 € (inkl. MwSt., kostenlos versandt)


Amazon (priz24), versendet 26-05-2026:
   2× Phoenix 3209549   PT 2,5-TWIN (Push-in, 3-polig: 1 IN + 2 OUT)
                        — je 9,06 €, gesamt ~18 €
                        — für Klemmen #1 (BFT 60) und #4 (BFT 63)


Noch zu bestellen:
   1× Waveshare ESP32-S3-POE-ETH-8DI-8RO
   1× Anhängerkabel 13×0,5 mm² (5 m, für Tor-Strecke + Verteiler-Innenverdrahtung
                                  mit durchgehender Farbcodierung)
```

## 11. Notizen zur Anlage

- **Standort:** geschützter Schuppen, trocken, Distanz Tor↔Verteiler < 1 m
- **Verteilung:** 3×12 TE (FIBOX MCE65 36M)
- **Netzwerk:** PoE-Switch im Netzwerkschrank vorhanden (vorhandenes Cat-Kabel zum Schuppen)
- **Vorgängersystem:** 3× Shelly Uni Plus mit schwachem WLAN-Empfang (zentraler Grund für Umbau)
- **Original-Finder (8 Stück 34.51.7.024.0010 + Sockel 93.01.7.024):** bleiben bis Migration im Betrieb; parallel wird das neue System aufgebaut

---

**Bei nächster Session:** Diese Datei lesen für vollen Kontext.

**Nächste konkrete Schritte (Priorität):**
1. **Waveshare ESP32-S3-POE-ETH-8DI-8RO bestellen** (Waveshare-Shop, AliExpress oder Amazon)
2. **Anhängerkabel 13×0,5 mm² (5 m)** bei Amazon bestellen
3. Bei Wareneingang der automation24- und Amazon-Sendung: **Aufbau im FIBOX-Verteiler** nach Layout
4. Sobald Anhängerkabel da: **Aderfarben festlegen** und in CLAUDE.md ergänzen
5. **ESPHome-YAML** schreiben sobald ESP da
6. **HA-Automationen** (Cover-Entity, Dauerauf-Logik, LED-Blink) parallel zur Software-Inbetriebnahme

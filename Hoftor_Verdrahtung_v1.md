# Hoftor-Steuerung — Verdrahtungs- & Belegungsdokumentation

**Version 1.0 — Stand 03-06-2026**

Verteiler-Innenausbau · FIBOX MCE65 36M (3×12 TE) · BFT Thalia BT A80/A160 + EBD

**Querverweise:**

- **Firmware-/Software-Logik (ESPHome):** siehe `Hoftor_Dokumentation_v0.35.docx` (Steuerkanäle, Scripts, Auto-Close, Störungserkennung, DI/Relais-Logik).
- **Live-Arbeitsdoku (vollständig, versioniert):** `CLAUDE.md` im Projektordner `esp/hoftor` (Abschnitt §6a = Belegungsplan).

---

## ⚠️ Sicherheit — vollständiges Spannungsfrei-Schalten

Der lokale Ausschalter (ABB) trennt **NUR den 24-V-Kreis dieser Steuerung** (PSU → R-/Bl-Block → RIF-0-Spulen, LEDs). **Nicht** abgeschaltet werden:

1. **ESP** — per PoE vom Netzwerk-Switch versorgt (isoliertes SELV ~48 V an der RJ45-Buchse).
2. **BFT-Controller** — hat eine **eigene 230-V-Versorgung**, unabhängig vom Ausschalter. Dadurch können die **Reihenklemmen 1–10 (BFT-Seite) Spannung führen** — insbesondere 1–6, da die BFT an ihren IC-Eingängen (60–65) ihre interne Sensorspannung gegen COM anlegt — **auch bei abgeschaltetem 24-V-Kreis**.

**Vollständig spannungsfrei nur mit allen drei Schritten:** (a) lokaler Ausschalter AUS · (b) ESP-Netzwerkkabel ziehen (oder PoE am Switch deaktivieren) · (c) BFT-Controller separat spannungsfrei schalten.

## 1. Zweck dieses Dokuments

Dieses Dokument beschreibt den **physischen Aufbau und die Verdrahtung** im Verteiler (Reihenklemmen, Koppelrelais, Potentialverteilung, Brücken, Aderfarben). Die **Steuerungs-/Firmware-Logik** ist bewusst NICHT hier, sondern in der Firmware-Doku (`Hoftor_Dokumentation_v0.35.docx`) beschrieben.

**Stand der Arbeiten (03-06-2026):** Der Verteiler-Innenausbau ist verdrahtet und per Foto verifiziert. Offen sind ESP-Seite, Tor-Adern (AHK-Kabel), LED-/Taster-Geräte und die 230 V-/24 V-Versorgung — siehe Abschnitt 13.

## 2. Durchgehende Nummerierung

| Nummern | Bauteil | Funktion |
|---|---|---|
| **1–10** | Reihenklemmen (8× PT 2,5 + 2× TWIN an #1/#4) | Tor-Anbindung (AHK-Kabel von der BFT) |
| **11–20** | 10× RIF-0 Koppelrelais | 9 belegt + Pos. 20 Reserve |
| **21–26** | 6 Klemmen (Block C) | LED blau/rot + Taster |
| **27–28** | 2 Sicherungshalter | 27 = 24 V-Hauptsicherung 2 A T · 28 = Reserve |
| **Bl-a…m** | PTFIX blau | GND/0 V-Verteilung · a = Zuleitung (PSU−) |
| **R-a…m** | PTFIX rot | +24 V-Verteilung · a = Zuleitung (Sicherung 27) |

Die alten **F-Rollen (F1–F8)** bleiben als logischer Bezug für den Firmware-Code erhalten und sind in den Tabellen in Klammern angegeben.

## 3. Anschluss-Benennung (Klemmen-Ebenen)

Reihenklemmen 1–10: `<Nr>-O` = obere Push-in-Reihe, `<Nr>-U` = untere. TWIN (#1, #4) zusätzlich `<Nr>-M` = Mitte.

**Bedeutung (Kabeleinführung von unten):**

- **-U = Außen-/Tor-Seite** (AHK-Ader von der BFT, von unten)
- **-O = Innen-/Relais-Seite** (Funktionsfarben-Brücke zum RIF-0)
- **TWIN:** -U = COM-Eingang (unterer Einzelport), -O + -M = die 2 Abgänge zu den Relais
- Einheitlich: **oben = innen, unten = Tor**

Relais behalten die Phoenix-Bezeichnung A1, A2, 11, 14. Eindeutige Referenz: `Kl. 1-O` (Reihenklemme) vs. `R11-K11` (Relais).

## 4. Reihenklemmen Block A (1–10) — Belegung

`-O`/`-M` sind verdrahtet, `-U` (Tor-Seite) ist noch frei.

| Klemme | Funktion | -O (innen) | -M (TWIN) | -U (Tor, später) |
|---|---|---|---|---|
| 1 TWIN | COM Hauptplatine | Schwarz → R12-K14 | Schwarz → R14-K14 | AHK Schwarz ← BFT 60 |
| 2 | Open / Dauerauf | Gelb → R14-K11 | — | AHK Gelb ← BFT 61 |
| 3 | Close | Grün → R12-K11 | — | AHK Grün ← BFT 62 |
| 4 TWIN | COM EBD | Braun → R11-K14 | Braun → R13-K14 | AHK Braun ← BFT 63 |
| 5 | Schritt / Start E | Weiß → R13-K11 | — | AHK Weiß ← BFT 64 |
| 6 | Open (Impuls) | Grau → R11-K11 | — | AHK Grau ← BFT 65 |
| 7 | Status Tor offen (Signal) | Rot → R17-A1 | — | AHK Rot ← BFT 24 |
| 8 | Status Tor zu (Signal) | Rosa → R18-A1 | — | AHK Rosa ← BFT 26 |
| 9 | +24 V Rückleiter offen | Rot → von R-d (Einspeisung) | — | AHK (Farbe offen) → BFT 25 |
| 10 | +24 V Rückleiter zu | leer (FBS-Brücke von 9-O) | — | AHK Weiß-Blau → BFT 27 |

Hinweis: Klemme 10 erhält +24 V über die FBS 2-5 rot (brückt 9↔10). Die Farbe der +24 V-Rückleiter-Adern (9-U/10-U) ist noch in Prüfung (Blau-Zuordnung kollidiert mit der GND-Konvention).

## 5. Koppelrelais 11–20 — Belegung

A2 aller Relais = GND (durchgehende blaue Brücke 11–20, gespeist von Bl-b).

| Pos | F-Rolle | ESP | Funktion | A1 (Spule +) | K11 | K14 |
|---|---|---|---|---|---|---|
| 11 | F1 | r1 | Öffnen (BFT 65) | von ESP r1 (später) | Kl. 6 | Kl. 4 TWIN (COM EBD) |
| 12 | F2 | r2 | Schließen (BFT 62) | von ESP r2 (später) | Kl. 3 | Kl. 1 TWIN (COM Haupt) |
| 13 | F5 | r3 | Schritt (BFT 64) | von ESP r3 (später) | Kl. 5 | Kl. 4 TWIN (COM EBD) |
| 14 | F6 | r4 | Dauerauf/Ped (BFT 61) | von ESP r4 (später) | Kl. 2 | Kl. 1 TWIN (COM Haupt) |
| 15 | F7 | r5 | LED blau (Tor offen) | von ESP r5 (später) | +24 V (FBS 4-6 rot) | LED blau → Kl. 21 |
| 16 | F8 | r6 | LED rot (Dauerauf) | von ESP r6 (später) | +24 V (FBS 4-6 rot) | LED rot → Kl. 22 |
| 17 | F3 | →DI1 | Status Tor offen (BFT 24) | Kl. 7 (Signal) | +24 V (FBS 4-6 rot) | ESP DI1 (später) |
| 18 | F4 | →DI2 | Status Tor zu (BFT 26) | Kl. 8 (Signal) | +24 V (FBS 4-6 rot) | ESP DI2 (später) |
| 19 | – | →DI3 | Taster Dauerauf (Koppelrelais) | Kl. 26 (Weiß-Schwarz) | +24 V (R-h) | ESP DI3 (später) |
| 20 | – | – | Reserve (frei) | – | – | – |

## 6. Interne Brücken Klemme↔Relais (Funktionsfarbe)

**Verdrahtet + verifiziert (03-06-2026).** Adern auf der oberen Reihe -O/-M, untere Reihe -U bleibt frei für die Tor-Adern.

| Von | Farbe | Quelle | Nach |
|---|---|---|---|
| 6-O | Grau | AHK | R11-K11 |
| 4-O | Braun | AHK | R11-K14 |
| 4-M | Braun | AHK | R13-K14 |
| 3-O | Grün | Einzel | R12-K11 |
| 1-O | Schwarz | Einzel | R12-K14 |
| 1-M | Schwarz | Einzel | R14-K14 |
| 5-O | Weiß | Einzel | R13-K11 |
| 2-O | Gelb | Einzel | R14-K11 |
| 7-O | Rot | Einzel | R17-A1 |
| 8-O | Rosa | AHK | R18-A1 |

**Quellen-Regel:** Bei Farbgleichheit Einzelader (20 AWG) bevorzugen — schont das AHK-Kabel. Einzeladern vorrätig: Gelb, Schwarz, Grün, Blau, Weiß, Rot. Nur Grau, Braun, Rosa, Weiß-Blau aus dem AHK-Rest ernten.

## 7. Versorgungs-Stiche (R-/Bl-Block → Relais)

**Verdrahtet (03-06-2026).** `a` bleibt frei für die PSU-Zuleitung.

| Von | Farbe | Nach | Zweck |
|---|---|---|---|
| Bl-b | Blau | R11-A2 | speist blaue A2-Brücke → alle Relais-A2 = GND |
| R-b | Rot | R15-K11 | speist FBS 4-6 rot → K11 von 15–18 = +24 V |
| R-d | Rot | Kl. 9-O | +24 V Status-Rückleiter (via FBS 2-5 rot auf 10) |

## 8. Block C (21–26) — LED + Taster

Ebenen: -O = innen (verdrahtet), -U = Gerät/außen (LED/Taster, später).

| Klemme | Funktion | -O (innen) | Farbe | -U (Gerät, später) |
|---|---|---|---|---|
| 21 | LED blau (+) | ← R15-K14 | Rot | LED blau Anode |
| 22 | LED rot (+) | ← R16-K14 | Rot | LED rot Anode |
| 23 | LED blau (−) | ← Bl-d (GND), FBS 2-5 blau → 24 | Blau | LED blau Kathode |
| 24 | LED rot (−) | (via FBS von 23) | – | LED rot Kathode |
| 25 | Taster +24 V | ← R-f | Rot | Taster-Bein 1 |
| 26 | Taster Signal | → R19-A1 (Koppelrelais → DI3) | Weiß-Schwarz | Taster-Bein 2 |

## 9. Taster-Koppelrelais R19

Der externe Taster läuft über ein eigenes Koppelrelais (Designprinzip „alle Feld-I/O über Relais"). R19 ist wie ein Status-Relais verschaltet:

- A1 ← Kl. 26 (Taster-Signal, Weiß-Schwarz)
- A2 = GND (blaue Brücke)
- K11 = +24 V (R-h, eigener Stich — R19 liegt außerhalb der FBS 4-6)
- K14 → ESP DI3 (später)

Drücken: +24 V (Kl. 25) → Taster → Kl. 26 → R19-Spule zieht an → K11(+24 V) → K14 → DI3.

## 10. Steckbrücken-Inventar (verbaut)

| Brücke | Einsatz |
|---|---|
| FBS 4-6 rot | K11 der Relais 15–18 → +24 V-Sammelschiene |
| FBS 2-5 rot | Klemmen 9↔10 → gemeinsamer +24 V-Statusrückleiter |
| FBS 2-5 blau | Klemmen 23↔24 → LED-Kathoden auf GND |
| (blau durchgehend) | A2 der Relais 11–20 → GND |

## 11. Aderfarben-Mapping (AHK-Kabel 13×0,5 mm²)

Durchgehende Farbcodierung: eine Farbe = eine Funktion, von der BFT-Klemme bis zum RIF-0.

| PT-Klemme | BFT | Aderfarbe | Funktion |
|---|---|---|---|
| 1 (TWIN) | 60 | Schwarz | COM Hauptplatine |
| 2 | 61 | Gelb | Open (Dauerauf) |
| 3 | 62 | Grün | Close |
| 4 (TWIN) | 63 | Braun | COM EBD |
| 5 | 64 | Weiß | Start E (Schritt) |
| 6 | 65 | Grau | Open (Impuls) |
| 7 | 24 | Rot | Status Tor offen — Signal |
| 8 | 26 | Rosa | Status Tor zu — Signal |
| 9 | 25 | (Farbe offen) | Status offen — +24 V Rückleiter |
| 10 | 27 | Weiß-Blau | Status zu — +24 V Rückleiter |
| 11–13 | – | Weiß-Schwarz · Weiß-Rot · Orange ⚠️ | Reserve |

AHK-Adern vorhanden, aber noch nicht aufgelegt (Tor-Seite -U). Weiß-Schwarz ist intern für das Taster-Signal verwendet (Kl. 26 → R19-A1).

## 12. Designprinzipien

- **Alle Feld-I/O über Koppelrelais:** Jede Leitung, die in den Außenbereich geht (Befehle, Status, LEDs, Taster), läuft über ein RIF-0 → galvanische Trennstelle zwischen ESP (innen) und Außenbereich. Schützt bei Fehler draußen (Kurzschluss/Überspannung/Feuchte/EMV).
- **Durchgehende Farbcodierung:** Funktionsfarbe von der BFT-Klemme bis zum Relais; Innenbrücken in derselben Farbe (Einzelader bevorzugt, sonst AHK-Rest).
- **Verdrahtung mit Aderendhülsen:** Alle Adern feindrähtig → isolierte 0,5er Hülsen (~8 mm, trapez gecrimpt), eine Ader pro Öffnung.
- **AHK-Orange meiden:** Die orange AHK-Ader ähnelt zu sehr der roten Einzelader → Verwechslungsgefahr; Orange bleibt unbenutzt in der Reserve.

## 13. Offene Anschluss-Checkliste (ESP / Tor / 230 V)

**A) ESP-Seite** (Waveshare in Reihe 1, PoE, VIN frei):

- A1 von R11–R16 ← Onboard-Relais r1–r6 (geschaltetes +24 V, schwarz)
- Onboard-Relais-COMs (r1–r6) ← +24 V (R-Block)
- K14 von R17→DI1, R18→DI2, R19→DI3
- ESP DI-COM → GND (Bl-Block) — Pflicht
- PoE-Cat-Kabel an ESP-RJ45

⚠️ **Freischalten:** siehe Sicherheitshinweis am Dokumentanfang — der Ausschalter trennt nur den 24-V-Kreis; **ESP (PoE) und BFT (eigene 230-V-Versorgung) bleiben unabhängig spannungsführend** (BFT speist die Klemmen 1–10).

**B) Geräteseite Block C** (-U):

- LED blau: + → 21-U, − → 23-U
- LED rot: + → 22-U, − → 24-U
- Taster: Bein 1 → 25-U, Bein 2 → 26-U

**C) Tor-Seite — AHK-Adern auf -U der Klemmen 1–10:**

- 1-U Schwarz←BFT 60 · 2-U Gelb←61 · 3-U Grün←62 · 4-U Braun←63 · 5-U Weiß←64 · 6-U Grau←65 · 7-U Rot←24 · 8-U Rosa←26 · 9-U (offen)→25 · 10-U Weiß-Blau→27

**D) 230 V + 24 V-Versorgung:**

- 230 V L/N/PE (Block B) einführen
- 24 V-Netzteil auf Hutschiene (Reihe 1)
- PSU+ → Sicherung 27 → R-a (+24 V-Einspeisung)
- PSU− → Bl-a (GND-Einspeisung)
- Sicherung 28 = Reserve (falls ESP intern versorgt)

---

## 14. Querverweise

- **Firmware-/Software-Logik (ESPHome):** `Hoftor_Dokumentation_v0.35.docx`
- **Live-Arbeitsdoku / vollständiger Stand:** `CLAUDE.md` (`esp/hoftor`, Abschnitt §6a)
- **BFT-Handbuch:** `THALIA_DUO_BT_A80_A160.pdf` (im Repo)

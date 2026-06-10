# Hoftor — Test- & Inbetriebnahme-Checkliste

**Stand:** 10-06-2026 · **Stufe 1: ohne 24 V** (ESP lebt über PoE, Rest spannungsfrei)

## 0. Rahmen & Werkzeug

- **ESP** über **PoE** versorgt (live, Web-UI auf `192.168.200.40`).
- **24-V-Kreis bleibt AUS** (Glassicherung 27 **draußen**), **BFT + Tor + LEDs/Taster nicht angeklemmt**.
- Werkzeug: **Multimeter** (Ω / Durchgangspiep), **Duspol** (Spannungsfreiheit), **Brückendraht**.
- **Ziel Stufe 1:** Verdrahtung + ESP-Logik risikofrei prüfen. Was echte 24 V braucht (RIF-0-Kontakte K11/K14, echte DI-Signale, LEDs, BFT) → **Stufe 2** (siehe Ende).

> ⚠️ Vor allen Ω-/Durchgangsmessungen: 24-V-Kreis aus **und** alle ESP-Relais AUS (frischer Boot, `restore_mode: ALWAYS_OFF`).

---

## A. Spannungsfreiheit & Sicht (Duspol / Auge)

- [ ] **A1** Glassicherung in Halter **27 draußen**.
- [ ] **A2** Duspol: **R-Block ↔ Bl-Block spannungsfrei**; Stichprobe RIF-0 A1/A2.
- [ ] **A3** ESP **VIN-Klemme frei** (kein Draht), nur PoE.
- [ ] **A4** Sicht: alle Aderendhülsen sitzen, keine abstehenden Litzen, keine vergessene Brücke/Werkzeug im Schrank.

## B. Durchgangs- & Kurzschluss-Prüfung (Multimeter, 24 V aus, ESP-Relais AUS)

**Der wichtigste Teil vor jeder 24-V-Gabe.**

- [ ] **B1 KURZSCHLUSS-Check:** **R-Block ↔ Bl-Block → KEIN Durchgang** (hochohmig). Piept es / ~0 Ω → Fehler suchen, **nicht** weiter. (Hinweis: liegt zufällig ein ESP-Relais zu, Pfad über 1 Spule ≈ kΩ = ok; **0 Ω = echter Schluss**.)
- [ ] **B2** +24-V-Schiene zusammenhängend: **R-a (von 27-U) ↔ R-c / -e / -g / -i / -k / -m** je Durchgang.
- [ ] **B3** GND-Schiene: **Bl-a ↔ Bl-b / -c / -d** je Durchgang.
- [ ] **B4** RIF-0 **A2-Brücke**: Bl-Block ↔ **A2 von R11 … R20** je Durchgang (durchgehende blaue Brücke).
- [ ] **B5** RIF-0 **Spulen** A1↔A2 je Relais **11–19**: plausibler Spulenwiderstand (nicht ∞ = unterbrochen, nicht 0 = Schluss; baugleiche ≈ gleich).
- [ ] **B6** **Spulen-Antriebe (Position + Farbe):** CH1-NO↔R11-A1 (grau) · CH2↔R12 (grün) · CH3↔R13 (weiß) · CH4↔R14 (gelb) · CH5↔R15 (rot) · CH6↔R16 (rot) — je Durchgang.
- [ ] **B7** **COM-Einspeisung:** R-c↔CH1-COM · R-e↔CH2 · R-g↔CH3 · R-i↔CH4 · R-k↔CH5 · R-m↔CH6 — je Durchgang.
- [ ] **B8** **DI-Signaladern:** DI1↔R17-K14 (rot) · DI2↔R18-K14 (rosa) · DI3↔R19-K14 (weiß-schwarz) — je Durchgang.
- [ ] **B9** **DI-Quercheck:** DI1/DI2/DI3 untereinander **KEIN** Durchgang (nicht verbrückt).
- [ ] **B10** **DI-COM:** Bl-Block ↔ **COM** Durchgang · **COM ↔ DGND KEIN Durchgang** (Isolation bestätigt).

## C. ESP Boot, Flash, Netzwerk (PoE)

- [ ] **C1** PWR-LED am ESP an, PoE ok.
- [ ] **C2** Erreichbar? `ping 192.168.200.40` / Web öffnet. Falls **nicht** erreichbar → **USB-C-Flash** nötig (Image evtl. leer/alt).
- [ ] **C3** **v0.35 flashen** (OTA aus ESPHome-Builder; sonst USB-C). Nach Reboot wieder erreichbar.
- [ ] **C4** Diagnose-Karte: Verbindung (API) ✓ · Uptime läuft · Chip-Temp plausibel · IP `192.168.200.40` · MAC · ESPHome-Version.

## D. Relais-Kanal-Mapping (Web schalten + Multimeter; 24 V aus)

Pro Kanal im Web schalten → am Onboard-Relais **CHx COM↔NO Durchgang** prüfen (schließt) + Status-Punkt im Web. Bestätigt **Firmware rX → physisch CHx → R1x**. (Die Ader CHx-NO↔R1x-A1 ist statisch schon in B6 geprüft.)

> Vor D5/D6 beide Halte-Schalter (Dauerauf / Fußgänger-Dauerauf) **AUS** — sie sperren sonst die Buttons.

- [ ] **D1** „Ch1 — Dauerauf" **EIN** (hält r1) → `Ch1 — Relais` 🟢 + **CH1 COM↔NO Durchgang** → AUS = offen. *(r1 = CH1 = R11 Öffnen)*
- [ ] **D2** „Ch4 — Fußgänger Dauerauf" **EIN** (hält r4) → `Ch4 — Relais` 🟢 + **CH4** schließt. *(r4 = CH4 = R14)*
- [ ] **D3** „LED blau" **EIN** (r5) → `LED blau` 🔵 + **CH5** schließt. *(r5 = CH5 = R15)*
- [ ] **D4** „LED rot" **EIN** (r6) → `LED rot` 🔴 + **CH6** schließt. *(r6 = CH6 = R16)*
- [ ] **D5** „Ch2 — Schließen" **drücken** (1 s Puls) → kurzer Durchgangs-Piep an **CH2** + `Ch2 — Relais` kurz 🟢. *(r2 = CH2 = R12)*
- [ ] **D6** „Ch3 — auf-stopp-zu" **drücken** (1 s Puls) → Piep **CH3** + `Ch3 — Relais`. *(r3 = CH3 = R13)*

> ⚠️ Schließt beim Schalten ein **falscher** Kanal → CH↔r-Reihenfolge stimmt nicht → vor 24 V klären.

## E. DI-Logik per Software-Test-Schalter (Web-UI, ohne Hardware-Signal)

Gruppe „Test (Simulation)" — prüft die Firmware-Logik ohne 24 V / echte DI.

- [ ] **E1** „Test: DI1 Tor offen" **EIN** → `DI1 — Tor offen` = ON; LED-blau-Logik: **r5/CH5 schließt** (`LED blau` 🔵). Wenn „Ch1 — Auto-Schließ-Zeit" > 0 → „Ch1 — Auto-Schließ-Restzeit" zählt runter. AUS → r5 aus, Auto-Close stoppt.
- [ ] **E2** „Test: DI2 Tor zu" **EIN** → `DI2 — Tor zu` = ON.
- [ ] **E3** „Test: DI3 Taster" bei **DI1(test)=EIN** → „Ch1 — Dauerauf" **toggelt** (r1/CH1). Bei **DI1=AUS** → „Test: DI3" → **LED rot blinkt 5×** (r6/CH6 5× kurz, per Web-Status/Multimeter beobachtbar), Dauerauf bleibt aus (Sicherheits-Sperre greift).
- [ ] **E4** *(optional)* Störungs-Logik: „Störung — Esk1-Schwelle" testweise **30 s**, beide Test-DI **AUS** + kein Halten → nach 30 s `Störung Eskalation 1` = ON + Schließen-Puls (r2/CH2 piept). „Test: DI2" **EIN** → quittiert. Schwelle wieder auf **180**.

## F. Abschluss Stufe 1

- [ ] **F1** Alle B-Checks bestanden (kein Kurzschluss, alle Pfade ok).
- [ ] **F2** Kanal-Mapping D korrekt (rX → CHx → R1x).
- [ ] **F3** DI-Logik E plausibel.
- [ ] Ergebnisse / Auffälligkeiten notiert: ____________________

---

## Stufe 2 — späterer Termin, MIT 24 V (nur Vorschau)

1. Glassicherung 27 stecken → 24 V an. Duspol: R-Block = 24 V, Bl = 0 V; Sicherungs-LED prüfen.
2. RIF-0 **Klick** + **K11/K14-Schalttest** (Koppelrelais schalten jetzt echt).
3. LEDs anklemmen (Block C -U) → leuchten bei r5/r6.
4. **Echter DI-Test** über 24-V-Signal (BFT-Status / Taster, brückbar) → DI1/DI2/DI3 lesen.
5. BFT + Tor-Adern (-U Klemmen 1–10) anklemmen, BFT-Parametrierung, Parallel-/Live-Test.

> ⚠️ **Vollständiges Freischalten** = Ausschalter (Hager) AUS **+** ESP-Netzwerkkabel ziehen **+** BFT separat spannungsfrei (BFT speist die Klemmen 1–10 unabhängig). Siehe Sicherheitshinweis in `Hoftor_Verdrahtung_v1.md`.

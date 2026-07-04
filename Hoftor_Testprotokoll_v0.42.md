# Hoftor — Testprotokoll v0.42

> **Zweck:** Vollständige Abnahme aller Funktionen, Fehlerzustände und Zustandskombinationen.
> **Stand:** 04-07-2026 · Firmware `hoftor.yaml` v0.42 · ESP `192.168.200.40`
> **Voraussetzung:** ESP geflasht, BFT parametriert (61=IC=4, 65=IC=2), Tor voll verkabelt, HA-Keller erreichbar.
> **Legende:** ✅ Bestanden · ❌ Fehlgeschlagen · ⏳ Offen · — nicht getestet

---

## Vorbereitung

Vor dem Testbeginn sicherstellen:
- [ ] ESP Web-UI `http://192.168.200.40` erreichbar
- [ ] Live-Log im Web-UI geöffnet (Scrollt mit)
- [ ] Tor steht in **Grundstellung: geschlossen** (DI2=1, DI1=0)
- [ ] Kein Auto-Close aktiv für Ch1 oder Ch4 (auf 0 s setzen oder Wert notieren)
- [ ] Test-Schalter alle aus

---

## 1 — Grundfunktionen (Einzelbefehle aus Grundstellung)

### T-01 · Öffnen aus Grundstellung

| Feld | Wert |
|---|---|
| Ausgangszustand | Tor zu (DI1=0, DI2=1) |
| Aktion | `Öffnen`-Button drücken |
| Erwartetes Verhalten | r1 schaltet 1 s · Tor fährt auf · bei Endposition DI1=1, DI2=0 · blaue LED an |
| Prüfen | DI2 geht auf 0 während Fahrt · DI1 geht auf 1 bei Endlage · Log: `pulse_open fired` |
| Ergebnis | ⏳ | Datum | — |

---

### T-02 · Schließen aus Vollauf

| Feld | Wert |
|---|---|
| Ausgangszustand | Tor voll auf (DI1=1, DI2=0) |
| Aktion | `Schließen`-Button drücken |
| Erwartetes Verhalten | r2 schaltet 1 s · Tor fährt zu · bei Endposition DI2=1, DI1=0 · blaue LED aus |
| Prüfen | DI1 geht auf 0 · DI2 geht auf 1 · Log: `pulse_close fired` |
| Ergebnis | ⏳ | Datum | — |

---

### T-03 · Schritt (auf–stopp–zu)

| Feld | Wert |
|---|---|
| Ausgangszustand | Tor zu |
| Aktion | `Schritt`-Button 1× drücken |
| Erwartetes Verhalten | Tor fährt auf (kein Endschalter → keine Quittierung) |
| Aktion 2 | `Schritt` erneut während der Fahrt |
| Erwartetes Verhalten 2 | Tor stoppt |
| Aktion 3 | `Schritt` erneut |
| Erwartetes Verhalten 3 | Tor fährt zu |
| Prüfen | r3 schaltet je 1 s · Log: `pulse_step fired` (3×) |
| Ergebnis | ⏳ | Datum | — |

---

### T-04 · Fußgänger (Ped, Impuls) aus Grundstellung

| Feld | Wert |
|---|---|
| Ausgangszustand | Tor zu (DI1=0, DI2=1) |
| Aktion | `Fußgänger`-Button drücken |
| Erwartetes Verhalten | r4 schaltet 1 s · linker Flügel fährt auf · DI1=0, DI2=0 (Ped-Zustand) · `g_ped_aktiv` = true (Log) · **kein** Auto-Close durch BFT |
| Prüfen | DI2 geht auf 0 · DI1 bleibt 0 · blaue LED bleibt aus · Log: `g_ped_aktiv set` |
| Warten | mind. 4 Minuten → Störungs-Erkennung darf **nicht** feuern |
| Ergebnis | ⏳ | Datum | — |

---

### T-05 · Ped schließen (nach T-04)

| Feld | Wert |
|---|---|
| Ausgangszustand | Ped offen (DI1=0, DI2=0) |
| Aktion | `Schließen`-Button drücken |
| Erwartetes Verhalten | Tor fährt zu · DI2=1 · `g_ped_aktiv` = false (Log) · blaue LED bleibt aus |
| Prüfen | Log: `g_ped_aktiv reset` · DI2 geht auf 1 |
| Ergebnis | ⏳ | Datum | — |

---

## 2 — Dauerauf / Ped-Dauerauf

### T-06 · Dauerauf einschalten (Tor zu)

| Feld | Wert |
|---|---|
| Ausgangszustand | Tor zu |
| Aktion | `Dauerauf`-Schalter EIN |
| Erwartetes Verhalten | r1 wird gehalten (Dauerauf aktiv) · Tor fährt auf · rote LED an · bei Endlage DI1=1 |
| Prüfen | rote LED leuchtet dauerhaft · Log: `dauerauf turned on` |
| Ergebnis | ⏳ | Datum | — |

---

### T-07 · Dauerauf ausschalten

| Feld | Wert |
|---|---|
| Ausgangszustand | Dauerauf aktiv, Tor offen |
| Aktion | `Dauerauf`-Schalter AUS |
| Erwartetes Verhalten | Nach ~1 s: `pulse_close` → Tor fährt zu · rote LED aus |
| Prüfen | Log: `dauerauf turned off` → `hold_close` → `pulse_close fired` |
| Ergebnis | ⏳ | Datum | — |

---

### T-08 · Verriegelung: Dauerauf + Ped-Dauerauf gleichzeitig

| Feld | Wert |
|---|---|
| Ausgangszustand | Dauerauf aktiv |
| Aktion | `Fußgänger Dauerauf`-Schalter EIN |
| Erwartetes Verhalten | Dauerauf wird automatisch ausgeschaltet · Ped-Dauerauf übernimmt |
| Prüfen | Log zeigt Verriegelungs-Logik · nur ein Halten gleichzeitig aktiv |
| Ergebnis | ⏳ | Datum | — |

---

### T-09 · Ped-Dauerauf ausschalten

| Feld | Wert |
|---|---|
| Ausgangszustand | Ped-Dauerauf aktiv |
| Aktion | `Fußgänger Dauerauf`-Schalter AUS |
| Erwartetes Verhalten | Nach ~1 s: `pulse_close` · Tor fährt zu · rote LED aus |
| Prüfen | Log: `ped_halten turned off` → `pulse_close fired` |
| Ergebnis | ⏳ | Datum | — |

---

## 3 — Zustandskombinationen (kritisch)

### T-10 · Öffnen während Ped aktiv

| Feld | Wert |
|---|---|
| Ausgangszustand | Ped offen (DI1=0, DI2=0, `g_ped_aktiv`=true) |
| Aktion | `Öffnen`-Button drücken |
| Erwartetes Verhalten | BFT öffnet voll (2. Impuls auf Kanal 65) · DI1 geht auf 1 · `g_ped_aktiv` reset durch DI1=1 |
| Prüfen | DI1=1, DI2=0 nach Fahrt · Log: `g_ped_aktiv reset` |
| Hinweis | BFT-Verhalten bei „Ped → Öffnen"-Sequenz beobachten (fährt durch oder öffnet neu?) |
| Ergebnis | ⏳ | Datum | — |

---

### T-11 · Ped drücken während Tor voll offen

| Feld | Wert |
|---|---|
| Ausgangszustand | Tor voll auf (DI1=1, DI2=0) |
| Aktion | `Fußgänger`-Button drücken |
| Erwartetes Verhalten | BFT-Verhalten beobachten (je nach Parametrierung: Ignorieren oder Reagieren) · `g_ped_aktiv` = true |
| Prüfen | Verhält sich BFT wie erwartet? DI1/DI2-Wechsel protokollieren |
| Ergebnis | ⏳ | Datum | — |

---

### T-12 · Schließen während Dauerauf aktiv

| Feld | Wert |
|---|---|
| Ausgangszustand | Dauerauf aktiv, Tor offen |
| Aktion | `Schließen`-Button drücken |
| Erwartetes Verhalten | Dauerauf schaltet ab · Schließen-Impuls wird ausgeführt · Tor fährt zu |
| Prüfen | Log zeigt korrekte Reihenfolge: Dauerauf off → pulse_close |
| Ergebnis | ⏳ | Datum | — |

---

### T-13 · Öffnen während Tor in Fahrt (zu → auf)

| Feld | Wert |
|---|---|
| Ausgangszustand | Tor fährt gerade auf |
| Aktion | `Öffnen`-Button drücken |
| Erwartetes Verhalten | Zweiter Impuls an BFT (je nach BFT-Parametrierung: stopp oder ignoriert) |
| Prüfen | Kein ESP-Absturz · Log: `pulse_open fired` |
| Ergebnis | ⏳ | Datum | — |

---

### T-14 · Schließen während Tor in Fahrt (auf → zu)

| Feld | Wert |
|---|---|
| Ausgangszustand | Tor fährt gerade zu |
| Aktion | `Schließen`-Button drücken |
| Erwartetes Verhalten | BFT reagiert (stopp oder weiter) |
| Prüfen | Kein ESP-Absturz |
| Ergebnis | ⏳ | Datum | — |

---

### T-15 · Ped während Dauerauf

| Feld | Wert |
|---|---|
| Ausgangszustand | Dauerauf aktiv, Tor offen |
| Aktion | `Fußgänger`-Button drücken |
| Erwartetes Verhalten | Ped-Impuls an BFT · `g_ped_aktiv` = true · Dauerauf bleibt aktiv (keine Interaktion) |
| Prüfen | rote LED bleibt an · Log: `g_ped_aktiv set` und `pulse_ped fired` |
| Ergebnis | ⏳ | Datum | — |

---

### T-16 · Taster Dauerauf (DI3) bei Tor zu

| Feld | Wert |
|---|---|
| Ausgangszustand | Tor zu (DI1=0, DI2=1) |
| Aktion | Taster am DI3 drücken |
| Erwartetes Verhalten | rote LED blinkt 5× (Verweigerung) · kein Öffnen · Dauerauf wird **nicht** aktiviert |
| Prüfen | Log: `blink_rot_5x` · Dauerauf-Status bleibt false |
| Ergebnis | ⏳ | Datum | — |

---

### T-17 · Taster Dauerauf (DI3) bei Tor offen

| Feld | Wert |
|---|---|
| Ausgangszustand | Tor voll auf (DI1=1, DI2=0) |
| Aktion | Taster am DI3 drücken |
| Erwartetes Verhalten | Dauerauf wird aktiv · rote LED an |
| Prüfen | Log: `dauerauf turned on via DI3` |
| Ergebnis | ⏳ | Datum | — |

---

## 4 — Auto-Close

### T-18 · Auto-Close Ch1 (Voll-Öffnen)

| Feld | Wert |
|---|---|
| Vorbereitung | Auto-Close Ch1 auf 30 s setzen |
| Ausgangszustand | Tor zu |
| Aktion | `Öffnen`-Button drücken |
| Erwartetes Verhalten | Tor fährt auf · nach 30 s ab DI1=1: automatisch `pulse_close` → Tor fährt zu |
| Prüfen | Timer läuft ab DI1=1 · Log: `auto_close_ch1 fired` |
| Nachher | Auto-Close wieder auf 0 s zurücksetzen |
| Ergebnis | ⏳ | Datum | — |

---

### T-19 · Auto-Close Ch1 via Funk (Hörmann)

| Feld | Wert |
|---|---|
| Vorbereitung | Auto-Close Ch1 auf 30 s |
| Ausgangszustand | Tor zu |
| Aktion | Hörmann-Funk-Taste (löst Öffnen aus) |
| Erwartetes Verhalten | DI1 geht auf 1 → Auto-Close-Timer startet auch ohne ESP-Befehl |
| Prüfen | Auto-Close feuert nach 30 s · Log zeigt Timer-Start bei DI1-Flanke |
| Hinweis | Auto-Close ist DI1-getriggert, nicht befehls-getriggert → funktioniert auch bei Funk-Öffnung |
| Ergebnis | ⏳ | Datum | — |

---

### T-20 · Auto-Close Ch4 (Ped)

| Feld | Wert |
|---|---|
| Vorbereitung | Auto-Close Ch4 auf 30 s |
| Ausgangszustand | Tor zu |
| Aktion | `Fußgänger`-Button drücken |
| Erwartetes Verhalten | Nach konfigurierten Sekunden: `pulse_close` · g_ped_aktiv wird durch DI2=1 reset |
| Prüfen | Timer startet nach Ped-Impuls · Schließen erfolgt automatisch |
| Nachher | Auto-Close Ch4 wieder auf 0 s |
| Ergebnis | ⏳ | Datum | — |

---

## 5 — Störungs-Erkennung & Eskalation

### T-21 · Störungs-Erkennung normal (DI1=DI2=0 > 180 s)

| Feld | Wert |
|---|---|
| Vorbereitung | `Test: DI2 Tor zu`-Schalter AUS lassen · Auto-Close = 0 · Dauerauf = aus · g_ped_aktiv = false |
| Ausgangszustand | Tor in Zwischenstellung (DI1=0, DI2=0) – erzwungen durch manuelles Stoppen |
| Erwartetes Verhalten | Nach 180 s: Störungs-Erkennung feuert → `pulse_close` (Esk1) |
| Prüfen | Log: `stoerung_erkannt` nach ~180 s · r2 schaltet |
| Ergebnis | ⏳ | Datum | — |

---

### T-22 · Eskalation (Esk2): Close-Reaktion bleibt aus

| Feld | Wert |
|---|---|
| Vorbereitung | Tor manuell in Zwischenstellung halten (BFT-Netz aus oder mechanisch blockiert) |
| Ausgangszustand | DI1=0, DI2=0 dauerhaft |
| Erwartetes Verhalten | 1. pulse_close → DI2 bleibt 0 → 2. pulse_close → DI2 bleibt 0 → 3. pulse_close → nach 3× kein DI2: Esk2-Alarm in HA (`binary_sensor: problem`) |
| Prüfen | Log zeigt 3 Close-Versuche · HA-Sensor `device_class: problem` geht auf `on` · Benachrichtigung in HA? |
| Ergebnis | ⏳ | Datum | — |

---

### T-23 · Störungs-Erkennung pausiert bei g_ped_aktiv

| Feld | Wert |
|---|---|
| Ausgangszustand | Ped offen (DI1=0, DI2=0, `g_ped_aktiv`=true) |
| Warten | 4 Minuten |
| Erwartetes Verhalten | Störungs-Erkennung feuert **nicht** · kein `pulse_close` im Log |
| Prüfen | Log bleibt ruhig · kein `stoerung_erkannt` |
| Ergebnis | ⏳ | Datum | — |

---

### T-24 · Störungs-Erkennung pausiert bei Dauerauf

| Feld | Wert |
|---|---|
| Ausgangszustand | Dauerauf aktiv, Tor offen (DI1=1, DI2=0) |
| Tor manuell stoppen | Tor in Zwischenstellung (DI1=0, DI2=0) – Dauerauf bleibt an |
| Warten | 4 Minuten |
| Erwartetes Verhalten | Störungs-Erkennung feuert **nicht** |
| Prüfen | Log: kein `stoerung_erkannt` |
| Ergebnis | ⏳ | Datum | — |

---

### T-25 · g_ped_aktiv Reset durch DI1=1

| Feld | Wert |
|---|---|
| Ausgangszustand | Ped offen (g_ped_aktiv=true) |
| Aktion | Vollöffnen-Befehl (Öffnen-Button) → DI1 geht auf 1 |
| Erwartetes Verhalten | `g_ped_aktiv` wird automatisch auf false gesetzt |
| Prüfen | Log: `g_ped_aktiv reset on DI1` |
| Ergebnis | ⏳ | Datum | — |

---

### T-26 · g_ped_aktiv Reset durch DI2=1

| Feld | Wert |
|---|---|
| Ausgangszustand | Ped offen (g_ped_aktiv=true) |
| Aktion | Schließen-Button → DI2 geht auf 1 |
| Erwartetes Verhalten | `g_ped_aktiv` wird auf false gesetzt |
| Prüfen | Log: `g_ped_aktiv reset on DI2` |
| Ergebnis | ⏳ | Datum | — |

---

## 6 — LEDs

### T-27 · Blaue LED (Tor offen)

| Feld | Wert |
|---|---|
| Aktion | Tor auf · dann zu |
| Erwartetes Verhalten | Blau an bei DI1=1 · Blau aus bei DI1=0 |
| Prüfen | LED reagiert unmittelbar auf DI1 |
| Ergebnis | ⏳ | Datum | — |

---

### T-28 · Rote LED (Halten aktiv)

| Feld | Wert |
|---|---|
| Aktion | Dauerauf EIN → AUS |
| Erwartetes Verhalten | Rot an während Dauerauf · Rot aus nach Abschalten |
| Aktion 2 | Ped-Dauerauf EIN → AUS |
| Erwartetes Verhalten 2 | Rot an während Ped-Halten |
| Prüfen | LED wechselt korrekt |
| Ergebnis | ⏳ | Datum | — |

---

### T-29 · 5× Blink rot (Taster-Verweigerung)

| Feld | Wert |
|---|---|
| Ausgangszustand | Tor zu (DI1=0) |
| Aktion | Taster DI3 drücken |
| Erwartetes Verhalten | Rote LED blinkt 5× schnell · kein Öffnen |
| Prüfen | Blink-Muster sichtbar |
| Ergebnis | ⏳ | Datum | — |

---

## 7 — Hörmann Funk

### T-30 · K1 Erkennung

| Feld | Wert |
|---|---|
| Aktion | Hörmann-Taste K1 drücken |
| Erwartetes Verhalten | DI7 geht kurz auf 1 · `binary_sensor.hoftor_funk_hormann_k1` in HA ändert Zustand |
| Prüfen | HA-Verlauf zeigt Flanke · ESP sendet **keinen** Befehl ans Tor |
| Ergebnis | ⏳ | Datum | — |

---

### T-31 · K2 Erkennung

| Feld | Wert |
|---|---|
| Aktion | Hörmann-Taste K2 drücken |
| Erwartetes Verhalten | DI8 geht kurz auf 1 · `binary_sensor.hoftor_funk_hormann_k2` in HA |
| Ergebnis | ⏳ | Datum | — |

---

## 8 — Boot-Verhalten

### T-32 · Kaltstart (kein ungewolltes Schließen)

| Feld | Wert |
|---|---|
| Ausgangszustand | Tor offen, alle Schalter aus |
| Aktion | ESP Strom trennen und wiederherstellen (oder `Restart` in Web-UI) |
| Erwartetes Verhalten | ESP bootet · **kein** `pulse_close` ausgelöst · Tor bleibt offen |
| Prüfen | Log nach Boot: kein `hold_close` · kein `pulse_close` · `dauerauf` und `ped_halten` starten im Zustand OFF (`DISABLED`) |
| Hinweis | Das war HT11-Bug (gefixt v0.39: `restore_mode: DISABLED`) |
| Ergebnis | ⏳ | Datum | — |

---

### T-33 · Boot-Indikator

| Feld | Wert |
|---|---|
| Aktion | ESP neu starten |
| Erwartetes Verhalten | Projektnamen / IP ca. 6 s nach Boot im Display (falls Display vorhanden) |
| Hinweis | Dieser ESP hat kein Display — entfällt |
| Ergebnis | — |

---

## 9 — Bench-Test (ohne Tor)

### T-34 · Test-Schalter „DI2 Tor zu"

| Feld | Wert |
|---|---|
| Aktion | `Test: DI2 Tor zu`-Schalter EIN |
| Erwartetes Verhalten | Störungs-Erkennung sieht DI2=1 → pausiert · kein Fehlalarm |
| Prüfen | Log: Störungs-Timer stoppt |
| Ergebnis | ⏳ | Datum | — |

---

## 10 — Zusammenfassung

| Test | Beschreibung | Ergebnis | Datum |
|---|---|---|---|
| T-01 | Öffnen Grundstellung | ⏳ | — |
| T-02 | Schließen aus Vollauf | ⏳ | — |
| T-03 | Schritt auf–stopp–zu | ⏳ | — |
| T-04 | Ped Impuls aus Grundstellung | ⏳ | — |
| T-05 | Ped schließen | ⏳ | — |
| T-06 | Dauerauf EIN | ⏳ | — |
| T-07 | Dauerauf AUS | ⏳ | — |
| T-08 | Verriegelung Dauerauf + Ped | ⏳ | — |
| T-09 | Ped-Dauerauf AUS | ⏳ | — |
| T-10 | Öffnen während Ped | ⏳ | — |
| T-11 | Ped während voll offen | ⏳ | — |
| T-12 | Schließen während Dauerauf | ⏳ | — |
| T-13 | Öffnen während Fahrt | ⏳ | — |
| T-14 | Schließen während Fahrt | ⏳ | — |
| T-15 | Ped während Dauerauf | ⏳ | — |
| T-16 | Taster DI3 bei Tor zu (Verweigerung) | ⏳ | — |
| T-17 | Taster DI3 bei Tor offen | ⏳ | — |
| T-18 | Auto-Close Ch1 | ⏳ | — |
| T-19 | Auto-Close Ch1 via Funk | ⏳ | — |
| T-20 | Auto-Close Ch4 (Ped) | ⏳ | — |
| T-21 | Störungs-Erkennung normal | ⏳ | — |
| T-22 | Eskalation Esk2 | ⏳ | — |
| T-23 | Störungs-Pause bei g_ped_aktiv | ⏳ | — |
| T-24 | Störungs-Pause bei Dauerauf | ⏳ | — |
| T-25 | g_ped_aktiv Reset via DI1 | ⏳ | — |
| T-26 | g_ped_aktiv Reset via DI2 | ⏳ | — |
| T-27 | Blaue LED | ⏳ | — |
| T-28 | Rote LED | ⏳ | — |
| T-29 | 5× Blink rot (Verweigerung) | ⏳ | — |
| T-30 | Hörmann K1 | ⏳ | — |
| T-31 | Hörmann K2 | ⏳ | — |
| T-32 | Kaltstart kein Schließen | ⏳ | — |
| T-34 | Test-Schalter DI2 | ⏳ | — |

---

> **Hinweis zum Ausfüllen:** Ergebnis ✅/❌ eintragen + Datum. Bei ❌ Beobachtung in Klammern notieren, z. B. `❌ (Tor schließt nicht, Log zeigt…)`.

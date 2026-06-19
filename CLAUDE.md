# Hoftor-Steuerung — Umbau Shelly → ESP

**Version:** 3.3
**Stand:** 19-06-2026
**Status:** ESP online + produktiv auf **`192.168.200.40`** (Ethernet). **ESPHome `hoftor.yaml` v0.39 — geflasht 19-06**, lebt **nur im Repo** `S:\Projekte\hw-hoftor\` (+ `hoftor_lcars.css` v0.8 + `hoftor_help.js`). ⚠️ **Hoftor gehört zur KELLER-HA (nicht DG)** → **kein Server-Sync**; NICHT auf den DG-Share `\\192.168.210.11\config\esphome\` laden (Florian flasht manuell / von der Keller-Instanz). **NEU 19-06-2026:** Funk-Empfänger **Hörmann HET/S 24 (BiSecur)** verdrahtet — K1→DI7 (grün), K2→DI8 (gelb), gespeist über **Sicherung 28** (+24-V-Reserve) via 4× 3er-Wago; reine Melder, Schalt-Logik in HA (`binary_sensor.hoftor_funk_hormann_k1/_k2`). Details: `Hoftor_Hoermann_Funkempfaenger_Uebergabe.md`. **Inbetriebnahme 19-06-2026:** ESP eingebaut + angeschlossen (PoE), AHK-Adern auf **UV-Klemmen 1–10 (-U)** aufgelegt (Farben bestätigt), 230-V-/24-V-Kette in Betrieb (Sicherungen **provisorisch 2× 0,5 A flink** statt träge), v0.39 geflasht + im Bench-Test. r2 (Schließen) auf **CH7/Pin 6** umgeklemmt (war Fehldiagnose HW-Glitch); **Boot-Close-Bug gefixt** — `restore_mode: DISABLED` an dauerauf/ped_halten (Default ALWAYS_OFF rief turn_off_action beim Boot → hold_close → r2/Close). ⚠️ **Noch offen:** BFT-/Tor-Seite der AHK-Adern auflegen (freie Enden in Berührungsschutz-WAGOs), Block-C-Geräteseite (LED/Taster -U), Live-Test, BFT-Parametrierung (61=IC6 Ped / 65=IC2 Open), HA-Automationen, Migration. Belegung §6a; Auflegeplan `Hoftor_AHK_Klemmenplan.html`.

**Implementierte Logik (Stand v0.35) — maßgeblich für Verdrahtung/Betrieb:**
- **PCA9554 @ 0x20** → 6 Relais = Öffnen (r1, BFT 65) / Schließen (r2, BFT 62) / Schritt (r3, BFT 64) / Fußgänger/Ped (r4, BFT 61) / **LED blau (r5, F7)** / **LED rot (r6, F8)**.
- **8× DI an GPIO4-11** (INPUT_PULLUP, inverted): Status Tor offen (DI1, BFT 24 via Koppelrelais F3), Status Tor zu (DI2, BFT 26 via Koppelrelais F4), **externer Taster Dauerauf (DI3)** (mit Sicherheits-Sperre: öffnet nie selbst, toggelt Dauerauf nur wenn Status Tor offen (DI1)=1, sonst `blink_rot_5x`), **DI7 = Funk Hörmann K1 / DI8 = Funk Hörmann K2** (HET/S 24, reine Melder, Logik in HA), DI4-DI6 Reserve.
- Ethernet **W5500/PoE** + feste IP **`192.168.200.40`** + native API (Noise) + OTA; `reboot_timeout: 0s`.
- **web_server v3** — Karten/Gruppen je Kanal, **LCARS-Farben** via `css_include: hoftor_lcars.css`, Live-Log.
- Befehle als **Buttons** (fix **1 s** Impuls, pulse_*-Scripts).
- **Dauerauf** (hält Öffnen (r1)) + **Fußgänger Dauerauf** (hält Fußgänger/Ped (r4)) — **AUS = nach 1 s Close** (`hold_close`-Puffer, abbrechbar). **Verriegelung = blockieren:** aktiver Hold sperrt den anderen, bis bewusst aus → nie 2 Relais gleichzeitig. Holds `optimistic:false` + explizites publish. **Block-Revert sichtbar:** gesperrter Hold lässt Web-Schalter zurückspringen.
- **Auto-Schließ-Zeit** je Öffnen (r1) / Fußgänger/Ped (r4) (0=aus). **Trigger = Status Tor offen (DI1)** (statt Button) → funktioniert auch bei Funk-Öffnung.
- **Button-Sperren** bei aktivem Halten (Öffnen bleibt bei Fußgänger Dauerauf aktiv = IC=6-Feature), je mit Log.
- **Status-Punkt** je Kanal (🟢 angezogen / 🔴 aus, event-getrieben via Öffnen (r1) / Schließen (r2) / Schritt (r3) / Fußgänger/Ped (r4) on_turn_on/off, kein Poll).
- **LED-Status-Logik:** LED blau (r5) ON bei Status Tor offen (DI1)=1, LED rot (r6) ON bei dauerauf||ped_halten. **LED-Blink:** `blink_rot_5x` (5×-Verweigerung 300 ms). LED-Status-Refresh-Script. **LEDs extern schaltbar** — manuelles Toggle wird beim nächsten Status-Trigger automatisch überschrieben (gewollt). **LED-Fehler-Endlos-Blinken bewusst NICHT** (`blink_fehler_start` + `g_fehler_aktiv` entfernt — Relais-Verschleiß, Nachbarn, ohne Reaktionsmöglichkeit nutzlos). Eskalation visuell/akustisch macht HA via Push/Alexa/Sonos.
- **Tor-Störungs-Erkennung:** 2 `number` (`stoer_esk1_sek` default 180 = 3 Min, `stoer_max_close_versuche` default 3) + 2 `binary_sensor` (`stoerung_esk1`/`stoerung_esk2`, `device_class: problem`). Interval 1 s: bei Status Tor offen (DI1)=0 AND Status Tor zu (DI2)=0 für > Schwelle → `pulse_close` (Schließen, r2) + counter++; bei counter ≥ max → Esk2. Pausiert bei `dauerauf=ON` oder `ped_halten=ON`. Quittierung automatisch sobald Status Tor offen (DI1)=1 oder Status Tor zu (DI2)=1.
- **Close-Reaktions-Check:** Script `check_close_reaktion` (mode: restart) prüft ob das Tor nach einem Close-Befehl reagiert (DI1 fällt von 1 auf 0). Gestartet von `autoclose_open` und `hold_close` wenn DI1=1. Wartet `stoer_esk1_sek` — reagiert Tor nicht → Esk1 + erneut `pulse_close` + Selbst-Neustart. Nach `stoer_max_close_versuche`: Esk2. Benutzt dieselben Sensoren+Parameter wie Störungs-Interval, läuft vollständig unabhängig davon. Global `g_close_reaktion_versuche`. Quittierung: DI1 on_release / DI2 on_press / dauerauf+ped_halten turn_on → stop + counter=0. Guard `g_close_reaktion_versuche==0` verhindert, dass das Störungs-Interval Esk1/Esk2 jede Sekunde während DI1=1 quittiert (Flackern). `autoclose_ped` läuft ohne `check_close_reaktion` (AUX16 bei Ped unklar, HT13).
- **Countdown-Restzeit-Sensoren:** 3 Template-Sensoren in Web-UI + HA — `autoclose_open_restzeit` (Öffnen, r1), `autoclose_ped_restzeit` (Fußgänger/Ped, r4), `stoer_esk1_restzeit`. Lesen Globals (`g_autoclose_open_ende_millis` / `g_autoclose_ped_ende_millis` / abgeleitet aus `g_letzter_endstatus_millis`), `update_interval: 1s`, `filter_out: nan` (NaN wird nicht publiziert, sonst Log-/Stream-Spam „nan s"; bei Inaktivität bleibt letzter Zahlenwert stehen, nach Boot „unbekannt" bis Script erstmals läuft). Auto-Close-Marker werden an allen 4 Stop-Stellen (Dauerauf-Ein, Ped-Halten-Ein, Schließen-Impuls (r2), Schritt-Impuls (r3), Status Tor offen (DI1)-Release) sauber auf 0 gesetzt. CSS bewusst nicht verändert, `web_server`-Log bleibt drin (Latenz nur bei offener Browser-Seite — irrelevant).
- **Hold-Timer-Stopp:** `dauerauf.turn_on` stoppt `autoclose_ped`, `ped_halten.turn_on` stoppt `autoclose_open` (sonst kann laufender Auto-Close-Timer `pulse_close` senden trotz aktivem Hold). BFT blockiert Close bei angezogenem Open-Relais; Stopp stellt zusätzlich sauberen Zustand + korrekten Countdown-Sensor-Wert sicher. Race Ch2/Ch3 + `hold_close` (1-s-Fenster): bewusst nicht gefixt (doppelter Close-Befehl harmlos, `pulse_close` mode:restart verlängert Impuls nur minimal).
- **Test-Simulation DI1/DI2/DI3:** Gruppe `grp_test` im Web-Interface + HA. 2 Template-Schalter `test_di1`/`test_di2` simulieren Endschalter offen/zu (pausieren Störungs-Eskalation, triggern LED-Logik + Auto-Close wie physische DIs). Test-Button `test_di3` repliziert Taster-Logik (Toggle Dauerauf wenn DI1=1, sonst blink_rot_5x). DI1/DI2: GPIO-Sensoren intern (`di1_raw`/`di2_raw`, Entprellfilter 50/100 ms) + Template-Binary-Sensor mit `lambda: raw.state || test.state` (update_interval: 200 ms). Alle on_press/on_release-Actions + Störungs-Interval laufen auf Template-Sensoren — transparent für restliche Logik.
- **Bedien-Anleitung über dem Log:** Anleitungs-Block in der RECHTEN Spalte (`#col_logs`, über dem Live-Log), per **`web_server: js_include: hoftor_help.js`** (DOM-Injektion, /0.js). **Warum JS:** `#col_logs` liegt im Shadow-DOM von `<esp-app>` — `css_include` durchdringt das nicht (nur CSS-Variablen/Farben), Entities können dort gar nicht hin (eigene Komponente `<esp-log>`). Beides am laufenden Gerät verifiziert. Das Script wartet aufs Rendern (Polling) + Re-Inject via MutationObserver. Lange Variante als `Hoftor_Kurzbeschreibung_Webinterface.md`.
- **Diagnose:** Verbindung(API), Uptime, Chip-Temperatur, IP/MAC, ESPHome-Version.
- **ℹ️ Info-Texte je Bedienelement** (direkt darunter, interleaved sorting_weight; beim Boot gesetzt). Diagnose = 1 Sammeltext. (19 alte `i_*`-Info-Text-Sensoren `internal:true` → komplett entfernt, nicht mehr in HA.) `device_class: opening` aus `di2_tor_zu` entfernt (zeigte Tor-ZU fälschlich als „Open").

**Entscheidungen fix (28-05):** TCA **aus** (ESP schließt aktiv) · Ped-Kanal = **IC=6 Timer Ped** · ESP sieht **keine Funk-Befehle** → Zustand kommt aus DI · Dauer-Zu verworfen.

**Offen am ESP (Code, PC):**
- ✅ Server-Sync erledigt 01-06-2026; ✅ v0.39 geflasht 19-06-2026 + Bench-Test. **Live-Test offen** (BFT-/Tor-Seite AHK + Block-C noch nicht aufgelegt).
- BFT-Ped-SCA-Frage (HT13): nach AUX16-Messung Lösung A (State-Machine) oder B (3. Statussignal SCA via freien EBD-AUX 22/23 + Koppelrelais + DI)
- Optional später: Auto-Schließ-Trigger Ch4 (Ped) auf passenden DI umstellen (wenn SCA verkabelt)

**Offen physisch (Tor/Verkabelung):**
- TWIN-Abschlussdeckel `D-PT 2,5-TWIN-MT` (3211317) ×3-4 bestellen (HT3b)
- FBS-Brücker für RIF-0 (A2-GND, K11-+24V) bestellen
- Verdrahtung nach PDF v2 + Aderfarben-Mapping (HT5)
- BFT-Parametrierung (Ped=IC=6, mOTOR=2, TEILOEFFN. M1 %)
- Parallel-Test mit Tor-Simulation
- Migration: Bestand abklemmen → ESP-System einklemmen
- ~~Schuppen-Klima BME280~~ verworfen 31-05 (Einbau im FIBOX → misst nur Gehäuse, nicht Schuppen-Luft).

**Offen HA-Seite (Keller-Master, read-only für Claude → Florian adoptiert):**
- `cover.hoftor` + Dauerauf-Logik + LED-Blink-Trigger (HT9)

## Cross-References (HA-Doku)

Dieses ESP-Projekt hat (geplante) HA-Berührungspunkte. Sobald in Betrieb, **auch aktualisieren**:
- `srv-ha-dachgeschoss/automatisierung.md` — geplant: Cover-Entity, Dauerauf-Logik, LED-Blink-Logik (HT9)
- `srv-ha-dachgeschoss/helfer_uebersicht.md` — geplant: ggf. Status-Helfer
- `srv-ha-dachgeschoss/infrastruktur.md` — geplant: ESPHome Waveshare ESP32-S3-POE-ETH
- `srv-ha-dachgeschoss/infrastruktur.md` — geplant: Hardware-Eintrag Hoftor-Steuerung
- `srv-ha-dachgeschoss/README.md` — ggf. Steuer-Karte
- Memory `project_hoftor_esp.md` — Pointer-Datei

## Bestellstatus (27-05-2026)

| Bestellung | Inhalt | Status |
|---|---|---|
| **automation24 #2026-3047210** | Phoenix-Klemmen + PTFIX + RIF-0 + Adapter + FBS 2-5 + FIBOX MCE65 36M | **angekommen 27-05-2026** ✅ |
| **Waveshare ESP32-S3-POE-ETH-8DI-8RO** | 1× Steuerung | **angekommen 27-05-2026** ✅ |
| **Amazon (priz24)** | 2× Phoenix PT 2,5-TWIN (Art. **3209549**, je 9,06 €) | unterwegs, Eintreffen 27.-28.5. ⏳ |
| **ETUKER Anhängerkabel 13×0,5** (5 m, 24,46 €) | Tor-↔-Verteiler + Innenverdrahtung mit durchgehender Farbe | bestellt, Eintreffen **Freitag 29-05-2026** ⏳ |
| **FBS-Brücker für RIF-0** | A2-Sammelschiene GND + K11-Sammelschiene +24V + Reserve grau | **noch zu bestellen** ⏳ |
| **Phoenix PT 4-HESILED 24** (3211903) + 2× D-ST 4 (3030420) | 1 + 2 | **HESI-Nachbestellung** (ersetzt generischen Halter) |
| **Glassicherung 1 A T 5×20** | 2–3 Stk | matcht 0,63-A-PSU |
| **Aderendhülsen 0,5 mm²** | bei Bedarf | im Bestand vorhanden |
| **H07V-K 0,5 mm²** | rot/blau/schwarz/grau/grün/gelb je 15 m | im Bestand vorhanden |

### Nachbestellung bei automation24 (finale Liste, abzgl. Bestand)

**Bestand aus Original-Bestellung #2026-3047210 (angekommen 27-05-2026):**
- 10× PT 2,5 grau, 2× D-ST 2,5, **1× CLIPFIX 35 (aktuell als ESP-Endhalter im Einsatz)**, 1× FBS 2-5 rot, 1× ZB 5 1-10
- 1× PTFIX rot + 1× PTFIX blau + 2× PTFIX-NS35, 8× RIF-0
- (CLIPFIX wird nicht für Klemmen-Blöcke gerechnet, da am ESP gebraucht)

```
KLEMMEN:
   5× Phoenix 3209510   PT 2,5             (grau, 4 für Block C LED+Taster + 1 für Block B L)
   1× Phoenix 3209523   PT 2,5 BU          (blau, N für 230V Block B)
   1× Phoenix 3209536   PT 2,5-PE          (grün-gelb, PE für 230V Block B)

ENDTEILE:
   1× Phoenix 3030417   D-PT 2,5-MT        (Endplatte für Block C; Block B nutzt 2. D-ST 2,5 aus Restbestand)
   9× Phoenix 3022218   CLIPFIX 35         (Endhalter)

PT 2,5 STECKBRÜCKE (LED-Block GND):
   1× Phoenix 3036877   FBS 2-5 BU         (blau, GND-Brücke LED-Kathoden)

BESCHRIFTUNG:
   1× Phoenix 1051003   ZB 5 UNBEDRUCKT    (für PT-Klemmen Block C, leer zum Selbstbeschriften)
   1× Phoenix          ZB 6 UNBEDRUCKT    (für RIF-0 F1-F8 Beschriftung)

FBS-BRÜCKER FÜR RIF-0:
   1× Phoenix 3032198   FBS 10-6 BU        (blau, A2-GND-Sammelschiene aller 8 RIF-0)
   1× Phoenix 3030255   FBS 4-6            (rot, K11-+24V-Sammelschiene F7+F8+F3+F4)

Gesamt: 9 Positionen, 19 Stück, ~25-30 € + Versand

Hinweise:
- Block B 230V: 3 Einzelklemmen (1× grau L + 1× blau N + 1× grün-gelb PE). PE endet ausschließlich in der Klemme — sofern das Phoenix-PSU Schutzklasse II ist, kein PE-Anschluss am Gerät nötig (am konkreten Gerät prüfen). FIBOX MCE65 36M ist Kunststoffgehäuse (keine Erdung erforderlich).
- Bestand-Klemmen (2× grau aus Original-Bestellung): wandern in Block C
- 2. D-ST 2,5 aus Bestand: wandert als Endplatte zu Block C
- Im Notfall können FBS-Brücker mit Seitenschneider gekürzt werden
```

**Nicht zu bestellen** — bereits im Bestand:
- 2× LED 24V (blau + rot) — aus laufender Shelly-Anlage übernommen
- 1× Taster — aus laufender Shelly-Anlage
- 8× Finder 34.51 — werden durch RIF-0 ersetzt (alte zu Reserve/Ausbau)

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

**Anleitung:** `THALIA_DUO_BT_A80_A160.pdf` (im Projektordner `hw-hoftor`, seit 03-06-2026 im Repo)

### Konfiguration BFT (im Display abgelesen, bestätigt)

| BFT-Klemme | Logik | Funktion |
|---|---|---|
| 60 | – | COM IC Hauptplatine |
| **61** | **IC1 = 6 (Timer Ped)** | Fußgänger/Ped (ESP Ch4/r4); gehalten = Ped-Dauerauf |
| **62** | **IC2 = 3 (Close)** | schließen (Impuls) |
| 63 | – | COM IC EBD |
| **64** | **IC3 = 0 (Start E)** | Schritt (auf/stopp/zu Impuls) |
| **65** | **IC4 = 2 (Open)** | öffnen (ESP Ch1/r1, Impuls); gehalten = Dauerauf |
| **24/25** | AUX = ? (Zustand offenes Tor) | Status Tor offen (potentialfrei) |
| **26/27** | AUX = ? (Status Tor geschlossen) | Status Tor zu (potentialfrei) |

**61 = Ped, 65 = Open (Festlegung, Stand 19-06-2026):** BFT 65 = **Öffnen** (ESP Ch1/r1, gehalten = Dauerauf), BFT 61 = **Fußgänger/Ped** (ESP Ch4/r4, gehalten = Ped-Dauerauf). Passt zu `hoftor.yaml` v0.37 + Innenverdrahtung (Gelb→61, Grau→65). ⚠️ Falls die BFT noch aus der früheren „beide IC=2 Open"-Redundanz kommt: **Klemme 61 am BFT-Display von IC=2 auf IC=6 (Timer Ped) umstellen** — sonst lösen „Öffnen" und „Fußgänger" vertauscht aus.

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

### Ped / Fußgänger = nur EIN Flügel (im Handbuch verifiziert 28-05-2026)
Quelle: Thalia-Handbuch S. 42/45/47/48. Jeder Steuereingang (Klemmen 61/62/64/65) ist frei auf eine der obigen Logiken stellbar.
- **IC=4 „Ped"** = *partielle Fußgängeröffnung* → öffnet **nur Motor 1 / einen Flügel** (Funktionsweise gemäß IMPULSFOLGE/Schritt-Logik). Voraussetzung: Logik **„mOTOR" = 2** (zweiflügelig). Bei 1-Flügel-Setup macht Ped eine Teilöffnung in % desselben Flügels.
- **Parameter `TEILOEFFN. M1 [%]`** (10–100 %, Default 100): wie weit Flügel 1 bei Ped aufgeht. Default 100 % = Flügel 1 ganz auf.
- **Parameter `ped TCA [s]`** (0–120, Default 0): eigene Auto-Schließzeit NUR nach Fußgänger-Manöver (0 = wie normales TCA).
- **IC=6 „Timer Ped"**: Fußgängeröffnung; Eingang gehalten → Flügel bleibt offen; wenn gehalten UND Open/Start kommt → volles Manöver, danach zurück zur Fußgängeröffnung; schließt auch nach Stromausfall.

**Umgesetzt (Festlegung):** Klemme 61 = **Ped** (IC=6 Timer Ped) = „nur ein Flügel / Fußgänger"; Klemme 65 bleibt **Open** (Vollöffnung, gehalten = Dauerauf). Firmware v0.37 entsprechend: Ch1/r1 = Öffnen (BFT65), Ch4/r4 = Fußgänger/Ped (BFT61). Dauerauf = gehaltenes Open auf Ch1; Ped-Dauerauf = gehaltenes Ped auf Ch4.

**⚠️ STATUS-LOGIK-PROBLEM bei Ped (Florian 28-05):** Tor-Status ist binär — AUX16 „Tor offen" → Status Tor offen (DI1), AUX13 „Tor zu" → Status Tor zu (DI2). Ped (ein Flügel) ist ein 3. Zustand. **Frage = was meldet AUX16 bei Ped?** MESSEN beim Test: schließt AUX16 schon „nicht-zu" (dann liest ESP „offen", kein Problem) ODER erst bei voll-offen (dann bei Ped **beide DIs (DI1 + DI2) = 0** = derselbe Zustand wie „fährt/Störung" in HT11 → Fehlalarm/ungewollter Close). Handbuch unklar.
- **Lösung A (keine HW):** ESP-State-Machine — ESP weiß, dass er Ped kommandiert hat → „beide 0" = „Fußgänger offen". Nur zuverlässig, wenn Ped NICHT auch per Funk-Handsender ausgelöst wird (ESP sieht Funk nicht).
- **Lösung B (robust, auch Funk):** 3. Statussignal **SCA** (BFT-AUX Logik 1 = Kontakt zu, sobald ein Flügel offen) → unterscheidet Ped sauber von Störung. Braucht freien EBD-AUX (z. B. 22/23) + Koppelrelais + freien DI — alles im Schuppen, keine Erdader.
- **HT11 (Fehlererkennung) + HT12 (Auto-Close) müssen den Ped-Zustand kennen**, sonst Fehlauslösung bei Fußgänger-Stellung.

### Grundsatz: ESP sieht keine Funk-Befehle (Florian 28-05)
Die BFT wird auch per **Funk-Fernbedienung** bedient — diese Befehle gehen **direkt an die BFT, der ESP bekommt sie NICHT mit**. Der ESP erfährt eine Zustandsänderung **nur über die Status-DIs** (Status Tor offen (DI1) / Status Tor zu (DI2)). **Konsequenzen:**
- Die ESP-Button-**Sperren** (v0.8) betreffen nur die ESP-Buttons — sie können das Tor nicht „verriegeln" (Funk geht immer).
- **Die Wahrheit über den Tor-Zustand kommt aus den Status-DIs (DI1 / DI2)**, NICHT aus der ESP-Befehls-Historie. HT11-Zustandslogik daher rein DI-basiert (offen/zu/fährt/Störung), nicht aus „was hat der ESP gesendet".
- **Entscheidungen fix 28-05:** TCA aus (ESP schließt aktiv), Ped-Kanal = IC=6 Timer Ped, Dauerauf/Fußgänger-Dauerauf via gehaltenem Relais.

### AUX-Belegung (Quercheck Handbuch)
AUX1 (20-21) Default Blinkleuchte; AUX2 (26-27) konfigurierbar; AUX11 (24-25, nur mit EBD-Karte). Status-Logiken: **13 = Status Tor geschlossen**, **16 = Zustand offenes Tor**. Unsere Nutzung (24/25 = Status Tor offen (DI1), 26/27 = Status Tor zu (DI2)) passt dazu.

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
- **Hager SBN225** (2-polig, 25 A, 1 TE) — Hand-Trennstelle (ersetzt früher geplanten „ABB Ausschalter"; verbaut 10-06-2026, lt. Foto)
- **Phoenix STEP POWER, Ord.-Nr. 1088495** (24 V / 0,63 A, ~2 TE) — 24 V DC SELV mit „DC OK"-LED (ersetzt früher geplantes DEWIN 1,5 A; ESP hängt per **PoE NICHT am PSU**, daher reicht 0,63 A locker — Last ~0,1–0,23 A)
- **Phoenix PT 4-HESILED 24** (3211903, 6,2 mm) — Sicherungs-Reihenklemme mit **Durchbrenn-LED** (ersetzt generischen Glassicherungshalter) + **Glassicherung 1 A T 5×20**. LED-Anzeige via **antiparallele LEDs** → Einspeiseseite/Polarität **egal**.
  - Endkappen: **2× Phoenix D-ST 4** (3030420) — beidseitig, da HESI-Klemme allein zwischen anderen Bauformen steht. (D-ST 4 ist 36,5 mm hoch, deckt nur den unteren stromführenden Anschlussbereich — Sicherungshalter oben ist konstruktiv selbst isoliert, korrekt so)
  - LED leuchtet bei durchgebrannter Sicherung + anliegender 24 V → Sofort-Diagnose
- → liefert 24 V DC SELV

### Potentialverteilung 24V
- **Phoenix PTFIX 6/12X2,5 RD** (Art. **3273356**) — +24V, 12 Abgänge à 2,5 mm²
- **Phoenix PTFIX 6/12X2,5 BU** (Art. **3273354**) — GND, 12 Abgänge
- **2× Phoenix PTFIX-NS35** (Art. **3274054**) — Tragschienen-Adapter (1 je PTFIX)

### Koppelrelais (Ersatz der 8 Finder)
- **Phoenix RIF-0-RPT-24DC/21** (Art. **2903370**) — All-in-One Koppelrelais, 24V DC Spule, Pickup ~17V, 6,2 mm Push-in, 1 Wechsler 6A
- **Verbaut: 10 Stück (Pos. 11–20)** — 9 belegt (F1–F8 + **R19 = Taster Dauerauf**) + **Pos. 20 Reserve** (nicht verplant). **Designprinzip: ALLE Feld-I/O über Koppelrelais** (galv. Trennung ESP innen ↔ Außenbereich). Belegung + Nummerierung siehe **§6a**.

### Reihenklemmen (Block 1 — externe Verbindung zur BFT)
- **8× Phoenix PT 2,5** (Art. **3209510**) — Push-in Durchgangsklemme grau
- **2× Phoenix PT 2,5-TWIN** (Art. **3209549**, von Amazon) — 1 Eingang + 2 Ausgänge, für Klemmen #1 (BFT 60) und #4 (BFT 63) wo 2 COMs gebraucht werden
- **1× Phoenix D-ST 2,5** (Art. **3030417**) — Endplatte (vom Shop als Zubehör zur PT 2,5 bestätigt)
- **1× Phoenix FBS 2-5** (Art. **3030161**) — Steckbrücke 2-polig, brückt GND-Klemmen 9↔10
- **2× Phoenix CLIPFIX 35** (Art. **3022218**) — Endhalter
- **1× Phoenix ZB 5 Zahlen 1-10** (Art. **1050025**) — Beschriftungsstreifen vorgedruckt

### ESP-Steuerung
- **Waveshare ESP32-S3-POE-ETH-8DI-8RO** — 10 TE, 8 Relais + 8 isolierte DI
- **Versorgung: PoE** (Strom + Daten über 1 Kabel vom vorhandenen PoE-Switch)
  - **VIN-Schraubklemme bleibt FREI** — kein 24V vom PSU an den ESP
  - **Begründung:** PoE-Switch + PoE-fähiges Board → würde man zusätzlich VIN anschließen, besteht reales Risiko dass VIN + PoE zusammentreffen (Umstöpseln, Port-Reset). Ob das Board VIN+PoE sicher ORt, ist NICHT im Datenblatt belegt. Daher: nur PoE, VIN gar nicht erst anschließen → Konflikt physisch ausgeschlossen.
  - **⚠️ Sicherheits-/Freischalt-Hinweis (Florian 03-06-2026):** Der lokale Ausschalter (ABB) trennt **NUR den eigenen 24-V-Kreis dieser Steuerung** (PSU → R-/Bl-Block → RIF-0-Spulen, LEDs). **NICHT** abgeschaltet sind: **(1) der ESP** (PoE vom Netzwerk-Switch, isoliertes SELV ~48 V an der RJ45-Buchse); **(2) der BFT-Controller** — der hat seine **eigene 230-V-Versorgung** und ist vom Ausschalter unabhängig. Dadurch können auch die **Reihenklemmen 1–10 / BFT-Adern Spannung führen** (insb. 1–6: die BFT legt an ihren IC-Eingängen 60–65 ihre interne Sensorspannung gegen COM an) — **auch wenn unser 24-V-Kreis aus ist**. **Vollständiges Freischalten = (a) Ausschalter AUS + (b) ESP-Netzwerkkabel ziehen / PoE am Switch aus + (c) BFT separat spannungsfrei.**
- **Galvanische Trennung (sauberste Architektur):**
  - ESP-Logik-Versorgung: PoE
  - 24V-Schaltkreis (RIF-0 Spulen, LEDs, DI-Schaltspannung): Phoenix-PSU
  - Verbindung ESP ↔ Schaltkreis nur über potentialfreie Relais-Kontakte + opto-isolierte DIs
- **Strombilanz:** PoE 802.3af bis 15W → ESP ~3-5W ✅. Phoenix-PSU 0,63 A; 24-V-Last (Relais + LEDs) ~0,1–0,23 A → ~3× Reserve ✅ (ESP per PoE, nicht am PSU)
- Ethernet-Config in ESPHome identisch (W5500), egal welche Versorgung

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

### ETUKER Anhängerkabel Tor ↔ Verteiler — 10 Adern (von 13)

| Ader / PT-Klemme# | BFT-Klemme | Funktion |
|---|---|---|
| 1 | 60 | COM Hauptplatine |
| 2 | 61 | Ped / Fußgänger (IC=6 Timer Ped) |
| 3 | 62 | Close |
| 4 | 63 | COM EBD |
| 5 | 64 | Start E (Schritt) |
| 6 | 65 | Open (Impuls) |
| 7 | 24 | Status Tor offen — Signal |
| 8 | 26 | Status Tor zu — Signal |
| 9 | 25 | Status Tor offen — Rückleiter (**+24V** mit neuer Topologie) |
| 10 | 27 | Status Tor zu — Rückleiter (**+24V** mit neuer Topologie) |

**Hinweis:** Klemmen 8 und 9 wurden **umsortiert** gegenüber natürlicher BFT-Reihenfolge, damit die beiden Rückleiter (9 und 10) adjacent sind → FBS 2-5 Brücker funktioniert.

**Topologie-Konvention (neu mit FBS-Brücker):**
- A2 aller RIF-0 = **GND** (via FBS 10-6 BU)
- A1 aller RIF-0 = **+24V wenn Spule aktiv** (geschaltet durch ESP-Relais oder BFT-Status-Kontakt)
- Status-Pärchen #9/#10 sind beide auf **+24V** (über FBS 2-5 rot gebrückt) — wenn BFT-Status-Kontakt schließt, kommt +24V von der Rückleiter-Klemme über den Schalter zur Signal-Klemme und damit zu F3-A1 bzw. F4-A1

### Phoenix Reihenklemmen-Anordnung (10 Stück)

```
[CF] [1-TWIN] [2-PT] [3-PT] [4-TWIN] [5-PT] [6-PT] [7-PT] [8-PT] [9-PT] [10-PT] [D]
       ↑                       ↑                                    └─FBS 2-5─┘
       BFT 60                  BFT 63                               (rot, +24V)
       → F2-11 + F6-11         → F1-11 + F5-11
       (über TWIN)             (über TWIN)
```

- TWIN-Klemmen an Position #1 und #4 (jeweils 1 Eingang + 2 Ausgänge)
- Normale PT 2,5 an Positionen #2, 3, 5, 6, 7, 8, 9, 10
- D-ST 2,5 Endplatte rechts; CLIPFIX 35 (CF) links + rechts als Endhalter
- FBS 2-5 rot zwischen 9 und 10 (gemeinsamer +24V-Rückleiter)
- ZB 5 Beschriftung mit Nummern 1-10

### Phoenix RIF-0 Anordnung (8 Stück) mit FBS-Brücker

```
Position:    1   2   3   4   5   6   7   8
            ┌──┬──┬──┬──┬──┬──┬──┬──┐
RIF-0:      │F1│F5│F2│F6│F7│F8│F3│F4│
            └──┴──┴──┴──┴──┴──┴──┴──┘
              ESP-Befehle      Lasten + Status

K11-Brücker: nicht durchgehend! (verschiedene Pegel pro Gruppe)
  - F7+F8+F3+F4: K11 = +24V (gemeinsam) → FBS 4-6 rot zwischen Pos. 5-8
  - F1+F5 K11 individuell zu unterschiedlichen BFT-Klemmen, kein Brücker
  - F2+F6 K11 individuell, kein Brücker
  (Wegen TWIN-Klemmen-Konzept reicht das Sammeln auf PT-Klemmen #1 + #4 aus)

A2-Brücker: durchgehend über alle 8 → FBS 10-6 BU blau (GND-Sammelschiene)

Die K11-Anschlüsse von F1/F5/F2/F6 gehen JEWEILS einzeln zu einer PT-Klemme:
  F1-K11 → PT-Klemme #6 (BFT 65 Open)
  F5-K11 → PT-Klemme #5 (BFT 64 Start E)
  F2-K11 → PT-Klemme #3 (BFT 62 Close)
  F6-K11 → PT-Klemme #2 (BFT 61 Open/Dauerauf)

K14 zu den COMs der BFT (über TWIN-Klemmen):
  F1-K14 → PT-Klemme #4 TWIN (BFT 63 COM EBD, gemeinsam mit F5-K14)
  F5-K14 → PT-Klemme #4 TWIN
  F2-K14 → PT-Klemme #1 TWIN (BFT 60 COM Hauptplatine, gemeinsam mit F6-K14)
  F6-K14 → PT-Klemme #1 TWIN

F7-K14 → LED blau Anode (mit 1kΩ Vorwiderstand → GND)
F8-K14 → LED rot Anode
F3-K14 → ESP Status Tor offen (DI1)
F4-K14 → ESP Status Tor zu (DI2)
```

### ESP-Pin → Phoenix RIF-0 → Tor-Funktion

| ESP-Pin | Relais | Funktion | Schaltet Kontakt zwischen (Phoenix-Anschluss) |
|---|---|---|---|
| Öffnen (r1) | **F1** | Befehl öffnen (Impuls, BFT 65) | K11=PT#6 (BFT 65), K14=PT#4 TWIN (BFT 63 COM-EBD) |
| Schließen (r2) | **F2** | Befehl schließen (Impuls, BFT 62) | K11=PT#3 (BFT 62), K14=PT#1 TWIN (BFT 60 COM-Haupt) |
| Schritt (r3) | **F5** | Befehl Schritt (Impuls, BFT 64) | K11=PT#5 (BFT 64), K14=PT#4 TWIN (BFT 63 COM-EBD) |
| Fußgänger/Ped (r4) | **F6** | Befehl Dauerauf/Ped (dauerhaft, BFT 61) | K11=PT#2 (BFT 61), K14=PT#1 TWIN (BFT 60 COM-Haupt) |
| LED blau (r5) | **F7** | LED blau ein (Tor offen) | K11=+24V (FBS 4-6), K14=LED blau Anode (mit 1kΩ Vorwiderstand → GND) |
| LED rot (r6) | **F8** | LED rot ein (Dauerauf aktiv) | K11=+24V (FBS 4-6), K14=LED rot Anode (mit 1kΩ Vorwiderstand → GND) |
| Status Tor offen (DI1) | **F3** | Status Tor offen lesen (BFT 24) | F3 schaltet: K11=+24V (FBS 4-6) → K14=ESP Status Tor offen (DI1) wenn BFT 24-25 schließt |
| Status Tor zu (DI2) | **F4** | Status Tor geschlossen lesen (BFT 26) | F4 schaltet: K11=+24V (FBS 4-6) → K14=ESP Status Tor zu (DI2) wenn BFT 26-27 schließt |
| externer Taster Dauerauf (DI3) | **R19** | Taster Dauerauf-Auslöser | Taster → Kl. 26 → R19-A1; R19-K14 → DI3 (Koppelrelais, Feld-I/O-Trennung) |
| Funk Hörmann K1 (DI7) | – | Hörmann HET/S 24 Kanal 1 (reine Meldung; Aktion frei in HA) | Empfänger-NO K1 → +24 V auf DI7 (GPIO10), grün; COM=+24 V via Sicherung 28/Wago |
| Funk Hörmann K2 (DI8) | – | Hörmann HET/S 24 Kanal 2 (reine Meldung; Aktion frei in HA) | Empfänger-NO K2 → +24 V auf DI8 (GPIO11), gelb |
| R7, R8 | – | Reserve (Waveshare-Onboard-Relais) |
| DI4–DI6 | – | Reserve |

### Phoenix RIF-0 Anschluss-Übersicht (alle 8) — NEUE Topologie mit FBS-Brücker

**Gemeinsam für alle 8 RIF-0:**
- **A2 → GND** (via FBS 10-6 BU Sammelschiene, 1 Ader vom PTFIX blau zur ersten A2)

**Befehls-Relais F1, F2, F5, F6** (ESP-getrieben, schalten Tor-Befehl):
- A1 → ESP-Relais Öffnen (r1) / Schließen (r2) / Schritt (r3) / Fußgänger/Ped (r4) (schaltet +24V vom PTFIX rot)
- A2 → **GND** (via FBS-Brücker)
- K11 → individuell zur jeweiligen BFT-Befehlsklemme (#2/#3/#5/#6)
- K14 → über TWIN-Klemme zur BFT-COM (#1 oder #4)

**LED-Relais F7, F8** (ESP-getrieben, schalten LED-Strom):
- A1 → ESP-Relais LED blau (r5) / LED rot (r6) (schaltet +24V)
- A2 → **GND** (via FBS-Brücker)
- K11 → **+24V** (via FBS 4-6 rot Sammelschiene, 1 Ader zum ersten K11=F7)
- K14 → LED-Anode (24V-Komplett-LED ohne externen Vorwiderstand)

**Status-Relais F3, F4** (BFT-getrieben, melden Status an ESP):
- A1 → Reihenklemme #7 bzw. #8 (BFT-Statussignal, wird +24V wenn BFT-Kontakt schließt)
- A2 → **GND** (via FBS-Brücker)
- K11 → **+24V** (via FBS 4-6 rot Sammelschiene, gemeinsam mit F7+F8)
- K14 → ESP Status Tor offen (DI1) bzw. Status Tor zu (DI2)

**Verdrahtungs-Ersparnis durch FBS-Brücker:**
- A2-GND-Sammlung: **1 Ader** statt 8 individueller Adern zum PTFIX blau
- K11-+24V-Sammlung (F7+F8+F3+F4): **1 Ader** statt 4 individueller Adern zum PTFIX rot

### Zusätzliche Pflicht-Verbindung — DI-COM des ESP

Die Waveshare DIs sind opto-isolierte Industrieeingänge mit einem **DI-COM-Sammelpin**. Damit die DIs +24V als Aktiv-Pegel erkennen, muss der DI-COM auf **GND** liegen:

```
PTFIX blau (GND) ──► Waveshare ESP DI-COM-Pin
```

→ **1 separate Ader** vom PTFIX blau zum ESP DI-COM (nicht über Block C). Ohne diese Verbindung erkennt der ESP keine DI-Signale.

## 6a. Belegungsplan — physische Nummerierung (Stand 03-06-2026)

**Verbaut im FIBOX, durchgehend nummeriert.** Diese physische Nummerierung ist die **Verdrahtungs-Referenz**. Die alten **F-Rollen (F1–F8)** bleiben als logischer Bezug für ESPHome-Code erhalten (in Klammern angegeben).

### Nummern-Übersicht

| Nummern | Bauteil | Funktion |
|---|---|---|
| **1–10** | Reihenklemmen (8× PT 2,5 + 2× TWIN an #1/#4) | Tor-Anbindung (AHK-Kabel von der BFT) |
| **11–20** | 10× RIF-0 Koppelrelais | 9 belegt (inkl. **R19 = Taster**) + **Pos. 20 Reserve** |
| **21–26** | 6 Klemmen (Block C) | LED blau/rot + Taster |
| **27–28** | 2 Sicherungshalter (PT 4-HESILED 24) | **beide aktuell 2× 0,5 A flink** (19-06-2026 gesteckt, **provisorisch** — 0,5 A träge nachrüsten). 27 = Hauptkreis: PSU+ → **27-O**, **27-U** → R-a · 28 = **Funk-Empfänger-Zweig** (Hörmann HET/S 24, war Reserve): PSU+ → 28-O, **28-U → Wago 1 (+24 V)** |
| **Bl-a…m** | PTFIX blau | GND/0V-Verteilung · **a = Zuleitung** (vom PSU−) |
| **R-a…m** | PTFIX rot | +24V-Verteilung · **a = Zuleitung** (von Sicherung 27) |
| (L/N/PE) | 230V-Einführung + Hager SBN225 (Trenner) + Phoenix STEP POWER 1088495 (24 V/0,63 A) | **verkabelt 10-06-2026** (230V→Hager→PSU→Sicherung→R-/Bl-Block) |

### Anschluss-Benennung (Klemmen-Ebenen)

**Reihenklemmen 1–10:** `<Nr>-O` = obere Push-in-Reihe, `<Nr>-U` = untere. **TWIN (#1, #4)** zusätzlich `<Nr>-M` = Mitte (3 Anschlüsse). Referenz oben/unten = wie verbaut (Beschriftungsstreifen mittig, Foto 03-06-2026).

Die **-O/-U-Bezeichnung (obere/untere Öffnung) gilt im ganzen Schrank** — auch Block C (21–26) und **Sicherungshalter 27/28** (z. B. **27-O = PSU+**, **27-U = R-a**). So ist pro Klemme sofort klar, welcher der beiden Anschlüsse gemeint ist.

**Bedeutungs-Konvention (Florian 03-06-2026 — Kabeleinführung von unten):**
- **-U = Außen-/Tor-Seite** (AHK-Ader von der BFT, kommt von unten rein, wird *später* aufgelegt)
- **-O = Innen-/Relais-Seite** (Funktionsfarben-Brücke zum RIF-0, *heute*)
- **TWIN: -U = COM-Eingang (AHK, einzelner unterer Port)** · **-O + -M = die 2 Abgänge zu den Relais (oberes Paar)** (O/M beliebig, gleiches Potential)
- Einheitlich: **oben = innen/Relais, unten = Tor**. → AHK kommt von unten auf -U, Innenverdrahtung auf -O bleibt unberührt.

**Relais 11–20** behalten die Phoenix-Bezeichnung **A1, A2, 11, 14**. Zur Eindeutigkeit immer mit Präfix: `Kl. 1-O` (Reihenklemme) vs. `R11-K11` (Relais).

### Relais-Belegung 11–20 (A2 aller = GND, durchgehend blau gebrückt)

| Pos | F-Rolle | ESP | Funktion | A1 (Spule +) | K11 | K14 |
|---|---|---|---|---|---|---|
| **11** | F1 | r1 | Öffnen (Impuls, BFT65) | von ESP r1 (+24V) | Klemme 6 (BFT65) | Klemme 4 TWIN (BFT63 COM-EBD) |
| **12** | F2 | r2 | Schließen (Impuls, BFT62) | von ESP r2 | Klemme 3 (BFT62) | Klemme 1 TWIN (BFT60 COM-Haupt) |
| **13** | F5 | r3 | Schritt/Start E (BFT64) | von ESP r3 | Klemme 5 (BFT64) | Klemme 4 TWIN (BFT63 COM-EBD) |
| **14** | F6 | r4 | Dauerauf/Ped (BFT61) | von ESP r4 | Klemme 2 (BFT61) | Klemme 1 TWIN (BFT60 COM-Haupt) |
| **15** | F7 | r5 | LED blau (Tor offen) | von ESP r5 | **+24V (FBS 4-6 rot)** | LED blau Anode → Klemme 21 |
| **16** | F8 | r6 | LED rot (Dauerauf) | von ESP r6 | **+24V (FBS 4-6 rot)** | LED rot Anode → Klemme 22 |
| **17** | F3 | →DI1 | Status Tor offen (BFT24) | Klemme 7 (BFT24-Signal) | **+24V (FBS 4-6 rot)** | ESP DI1 |
| **18** | F4 | →DI2 | Status Tor zu (BFT26) | Klemme 8 (BFT26-Signal) | **+24V (FBS 4-6 rot)** | ESP DI2 |
| **19** | – | →DI3 | **Taster Dauerauf** (Koppelrelais) | Klemme 26 (Taster-Signal, Weiß-Schwarz) | +24V (R-h, Rot) | ESP DI3 |
| **20** | – | – | Reserve (frei, nicht verplant) | – | – | – |

→ **K11-+24V-Gruppe = Pos. 15–18 adjacent** → **FBS 4-6 rot** brückt deren K11 gemeinsam auf +24V.
→ Befehlsrelais 11–14: K11 individuell zur BFT-Befehlsklemme, K14 via TWIN zur COM. A1 = ESP-Relais (geschaltetes +24V vom R-Block).
→ **R19 (Taster)** = wie Status-Relais: A1 ← Taster-Signal (Kl. 26), A2 = GND, **K11 = +24V (eigener Stich, NICHT unter FBS — R19 liegt außerhalb 15–18)**, K14 → ESP DI3.
→ Alle A2 → GND (durchgehende blaue Brücke über 11–20, vom Bl-Block gespeist).

**Designprinzip (Florian 03-06-2026): ALLE Feld-I/O laufen über Koppelrelais** — auch der Taster (DI3). Grund: alle Leitungen gehen in den **Außenbereich**, die Steuerung sitzt **innen** → jedes RIF-0 ist eine **galvanische Trennstelle**, die den ESP schützt, falls draußen ein Fehler auftritt (Kurzschluss/Überspannung/Feuchte/EMV) — unabhängig davon, ob technisch zwingend nötig. Konsequenz: Reserve = nur noch **R20** + DI4–DI6 + R7/R8 (DI7/DI8 = Funk Hörmann).

### Interne Brücken Klemme↔Relais (Funktionsfarbe) — ✓ verdrahtet 03-06-2026

**Status: alle 10 gesetzt + per Foto verifiziert** (R11–R14 K11/K14, R17/R18 A1). Adern auf oberer Reihe -O/-M, untere Reihe -U frei für Tor.

**Quellen-Regel (Florian 03-06-2026):** Bei **Farbgleichheit Einzelader (20 AWG) bevorzugen** — schont das AHK-Kabel. Einzeladern vorrätig: Gelb, Schwarz, Grün, Blau, Weiß, Rot. Farben ohne Einzelader (Grau, Braun, Rosa, Weiß-Blau) werden aus dem AHK-Reststück geerntet. Farbe = Funktionsfarbe der zugehörigen AHK-Ader → durchgehende Codierung bleibt erhalten.

**AHK-Orange meiden (Florian 03-06-2026):** Die orange AHK-Ader ähnelt zu sehr der roten Einzelader → Verwechslungsgefahr. Orange bleibt unbenutzt in der Reserve (Klemmen 11–13); für Innenbrücken/Reserve andere Farben bevorzugen.

**Verdrahtung mit Aderendhülsen (Entscheidung 03-06-2026):** Alle Adern sind feindrähtig (AHK-Litze + H07V-K) → **isolierte 0,5er Aderendhülsen** (~8 mm, trapez gecrimpt). Grund: feindrähtig ohne Hülse erfordert bei Phoenix Push-in das Drücken der Betätigung + spleißt bei 0,5 mm² → Hülse gibt direktes Push-in, gasdichten, vibrationsfesten Kontakt. **Eine Ader pro Öffnung** (TWIN + FBS lösen alle Doppelbelegungen → keine Zwillingshülsen nötig).

| Von Klemme | Farbe | Quelle | Nach |
|---|---|---|---|
| 6-O | Grau | **AHK** | Relais 11 (F1)-K11 |
| 4-O | Braun | **AHK** | Relais 11 (F1)-K14 |
| 4-M | Braun | **AHK** | Relais 13 (F5)-K14 |
| 3-O | Grün | Einzel | Relais 12 (F2)-K11 |
| 1-O | Schwarz | Einzel | Relais 12 (F2)-K14 |
| 1-M | Schwarz | Einzel | Relais 14 (F6)-K14 |
| 5-O | Weiß | Einzel | Relais 13 (F5)-K11 |
| 2-O | Gelb | Einzel | Relais 14 (F6)-K11 |
| 7-O | Rot | Einzel | Relais 17 (F3)-A1 |
| 8-O | Rosa | **AHK** | Relais 18 (F4)-A1 |

→ Die Tor-/Außenseite der Klemmen 1–10 (AHK-Adern von der BFT) wird **später** aufgelegt; heute nur die Innenbrücken zu den Relais.
→ Pro AHK-Farbe ~2 m durchgehend für die spätere Tor-Strecke reservieren, Innenbrücken vom Reststück ernten.

### Versorgungs-Stiche (R-/Bl-Block → Relais) — ✓ verdrahtet 03-06-2026

Speisen die gesetzten Sammelschienen (verifiziert per Foto). `a` bleibt frei für PSU-Zuleitung.

| Von | Farbe | Nach | Zweck |
|---|---|---|---|
| Bl-b | Blau | R11-A2 | speist blaue A2-Brücke → alle Relais-A2 = GND |
| R-b | Rot | R15-K11 | speist FBS 4-6 rot → K11 von 15–18 = +24V |
| R-d | Rot | Klemme 9-O | +24V Status-Rückleiter (via FBS 2-5 rot auf 10) |

### Block C — Klemmen 21–26 (LED + Taster)

Ebenen wie Hauptblock: **-O = innen** (Relais/Block, *heute*), **-U = Gerät/außen** (LED/Taster, *später* von unten).

| Klemme | Funktion | Innen (-O, heute) | Farbe | Außen (-U, später) |
|---|---|---|---|---|
| **21** | LED blau (+) | ← Relais 15 (F7)-K14 | Rot | LED blau Anode |
| **22** | LED rot (+) | ← Relais 16 (F8)-K14 | Rot | LED rot Anode |
| **23** | LED blau (−) | ← Bl-Block (GND), **FBS 2-5 blau** brückt 23↔24 | Blau | LED blau Kathode |
| **24** | LED rot (−) | (via FBS 2-5 blau von 23) | – | LED rot Kathode |
| **25** | Taster +24V | ← R-Block | Rot | Taster-Leg 1 |
| **26** | Taster Signal | → **R19-A1** (Koppelrelais, R19-K14 → DI3) | Weiß-Schwarz (AHK-Reserve) | Taster-Leg 2 |

**✓ verdrahtet + verifiziert 03-06-2026 (4 Adern, innen -O):** 21-O←R15-K14 (rot), 22-O←R16-K14 (rot), 23-O←Bl-d (blau), 25-O←R-f (rot). Anoden bestätigt nicht vertauscht (R15→21 blau, R16→22 rot), -U frei.

**✓ verdrahtet 03-06-2026 (Taster-Koppelrelais R19, 2 Adern):** Klemme **26-O → R19-A1** (Weiß-Schwarz) · **R-h → R19-K11** (+24V, Rot, eigener Stich). R19-A2 = GND (Brücke), R19-K14 → DI3 + Taster-Geräteseite (25-U/26-U) später.

### Vorhandene Steckbrücken (Inventar 03-06-2026)

| Brücke | Einsatz |
|---|---|
| **FBS 4-6 rot** | K11 der Relais 15–18 → +24V-Sammelschiene |
| **FBS 2-5 rot** | Klemmen 9↔10 → gemeinsamer +24V-Statusrückleiter |
| **FBS 2-5 blau** | Klemmen 23↔24 → LED-Kathoden auf GND |
| (blau durchgehend) | A2 der Relais 11–20 → GND (bereits gesetzt) |

> **Hinweis:** Die veralteten Schaltplan-PDFs (v1/v2) + Generator-Skripte wurden am 03-06-2026 entfernt (überholt + qualitativ unzureichend). Maßgebliche Verdrahtungs-Referenz ist dieser Belegungsplan (§6a) bzw. `Hoftor_Verdrahtung_v1.docx`.

### Noch offen — Anschluss-Checkliste (ESP / Tor / 230V)

Innenausbau (Befehle/Status/LED/Taster intern + Versorgungs-Stiche + R19) ist **fertig + verifiziert** (Stand 03-06-2026). Offen bleibt:

**A) ESP-Seite** (Waveshare in Reihe 1, PoE, VIN frei). **Waveshare = ESP32-S3-POE-ETH-8DI-8RO**; Relais-Klemmen je Kanal **NO–COM–NC** (COM mittig, am Aufdruck verifiziert; NO = bei Florians Einbau die linke Klemme, NC frei). Kanäle CH1=r1 … CH6=r6 (Zuordnung final erst nach Flash testen).
- [x] **Onboard-Relais-COMs CH1,CH3–CH7** ← +24 V (R-Block, **rot**), verdrahtet 10-06-2026: CH1←R-c · **CH7←R-e** (Schließen, v0.38 von CH2 umgezogen) · CH3←R-g · CH4←R-i · CH5←R-k · CH6←R-m. **CH2 unbenutzt** (R-e-Stich jetzt CH7-COM).
- [x] **NO CH1–CH6 → A1 von R11–R16** — verdrahtet 10-06-2026. **Antriebsfarbe = Funktionsfarbe des Kanals** (durchgängig BFT→Waveshare, ersetzt die alte „schwarz"-Festlegung): NO CH1→R11-A1 **Grau** (Öffnen) · **CH7**→R12 **Grün** (Schließen, v0.38 von CH2 umgeklemmt wg. Boot-Glitch) · CH3→R13 **Weiß** (Schritt) · CH4→R14 **Gelb** (Dauerauf/Ped) · CH5→R15 **Rot** (LED blau) · CH6→R16 **Rot** (LED rot). LEDs = Rot, da +24-V-Antrieb ohne BFT-Funktionsfarbe (Schwarz verworfen — würde mit COM-Haupt + „schwarz=GND"-Lesart kollidieren).
- [x] **K14 von R17→DI1** (Status offen, **rot**) · **R18→DI2** (Status zu, **rosa**) · **R19→DI3** (Taster, **weiß-schwarz**) — verdrahtet 10-06-2026, Funktionsfarbe durchgezogen
- [x] **ESP DI-COM → GND** — verdrahtet 10-06-2026: **Bl-c → COM** (Blau). **DGND bleibt frei** (= nicht-isolierte Logik-Masse; nur der isolierte Eingangs-**COM** wird auf den 24-V-GND gelegt). DIs sind bidirektionale Opto-Eingänge für aktives 24-V-Signal → Polarität unkritisch, Bestätigung beim Flash-Test.
- [ ] PoE-Cat-Kabel an ESP-RJ45 (VIN frei) — danach Flash + Kanal-/DI-Test

**B) Geräteseite Block C** (untere Reihe -U, von unten):
- [ ] LED blau: **+ → 21-U** · **− → 23-U**
- [ ] LED rot: **+ → 22-U** · **− → 24-U**
- [ ] Taster: Bein 1 **→ 25-U** (+24V) · Bein 2 **→ 26-U** (Signal)

**C) Tor-Seite — AHK-Adern auf -U der Klemmen 1–10** (von unten):
- [ ] 1-U Schwarz←BFT60 · 2-U Gelb←BFT61 · 3-U Grün←BFT62 · 4-U Braun←BFT63 · 5-U Weiß←BFT64 · 6-U Grau←BFT65 · 7-U Rot←BFT24 · 8-U Rosa←BFT26 · **9-U Blau→BFT25** · 10-U Weiß-Blau→BFT27

**D) 230V + 24V-Versorgung:** (Strang verdrahtet 10-06-2026: 230V-Klemmen → Hager SBN225 → Phoenix STEP POWER 1088495 → Sicherung 27 → R-Block · PSU− ungesichert → Bl-Block)
- [x] 230V L/N/PE (Block B) einführen → Hager SBN225 → PSU-Eingang (10-06-2026)
- [x] 24-V-Netzteil (**Phoenix STEP POWER 1088495**, 0,63 A) auf Hutschiene (Reihe 3, unten rechts) — ESP per PoE, NICHT am PSU — **verbaut 10-06-2026**
- [x] **27-U → R-a** verdrahtet (Rot 0,5 mm²)
- [x] **PSU+ → 27-O** verdrahtet (10-06-2026). Polarität egal (antiparallele LED). **Sicherungen gesteckt 19-06-2026: 2× 0,5 A flink** (provisorisch, da keine träge da; bei Gelegenheit 0,5 A träge nachrüsten).
- [x] **PSU− → Bl-a** (GND, **ungesichert** — 0-V-Rückleiter nie absichern) — verdrahtet 10-06-2026
- [ ] Sicherung 28 = **+24-V-Reserve** (leer)

## 6. Layout im Verteiler (3×12 TE FIBOX MCE65 36M) — 3 Klemmen-Blöcke

```
Reihe 1 — ESP-Steuerung (oben, 10 TE belegt, 2 TE Reserve)
┌──────────────────────────────────────────────────────┬───────────┐
│        Waveshare ESP32-S3-POE-ETH-8DI-8RO            │  Reserve  │
│              10 TE                                   │    2 TE   │
└──────────────────────────────────────────────────────┴───────────┘

Reihe 2 — Schaltlogik + 2 Klemmen-Blöcke (mitte, 8 TE belegt, 4 TE Reserve)
┌──────────────┬──────────────┬────────────┬──────────────────┐
│  9× RIF-0    │ Block A      │ Block C    │      Reserve     │
│ Koppelrelais │ Tor 10 Kl.   │ LED+Taster │                  │
│ (Pos.20 Res) │ (8 PT+2 TWIN)│ 6 Klemmen  │                  │
│    3 TE      │     3 TE     │   2 TE     │       4 TE       │
└──────────────┴──────────────┴────────────┴──────────────────┘

Reihe 3 — 230V + Versorgung (unten, ~10 TE belegt, 2 TE Reserve)
┌──────────┬──────────┬──────┬──────────────┬──────────┬─────────┐
│PTFIX blau│PTFIX rot │ Si.  │    Phoenix   │  Hager   │ Block B │
│  GND     │  +24 V   │27/28 │    PSU       │ SBN225   │  230V   │
│Verteiler │Verteiler │0,5 A │ 24V/0,63 A   │ 2-pol.   │  3 Kl.  │
│  2 TE    │  2 TE    │ 2 TE │    2 TE      │  1 TE    │  ~2 TE  │
└──────────┴──────────┴──────┴──────────────┴──────────┴─────────┘
                                                       L+N+PE ↑

Gesamt belegt: 28 TE | Reserve: 8 TE
```

### Drei Klemmen-Blöcke im Detail

**Block A — Tor-Anbindung (Reihe 2, links der Mitte)**
- 10 Klemmen: 8× PT 2,5 grau + 2× PT 2,5-TWIN (an Position #1 und #4)
- FBS 2-5 rot zwischen #9 und #10 (+24V Rückleiter-Brücke)
- 1× D-ST 2,5 + 2× CLIPFIX 35
- Externes Kabel: ETUKER Anhängerkabel 13×0,5 vom Tor (10 Adern genutzt, 3 Reserve)

**Block B — 230V-Eingang (Reihe 3, ganz rechts)**
- 3 Klemmen: PT 2,5 grau (L) + PT 2,5 BU (N) + PT 2,5-PE (PE)
- 1× D-ST 2,5 + 2× CLIPFIX 35
- Externes Kabel: 230V Hauszuleitung (NYM 3×1,5)

**Block C — LED + Taster (Reihe 2, rechts neben Block A)**
- 6 Klemmen alle grau:
  - #1 LED blau (+), #2 LED rot (+) ← geschaltete Anoden von F7/F8-K14
  - #3 LED blau (−), #4 LED rot (−) ← FBS 2-5 BU brückt zu GND
  - #5 Taster +24V, #6 Taster Signal → ESP externer Taster Dauerauf (DI3)
- 1× D-ST 2,5 + 2× CLIPFIX 35
- Externe Kabel: 2× zu LEDs (24V Industrie-Signalleuchten), 1× zum Taster

**Anordnung-Logik:**
- **ESP-Steuerung** oben (Reihe 1) — PoE-Cat-Kabel kurz zur RJ45
- **24 V Schaltlogik** in der Mitte (Reihe 2) — Block A + RIF-0 + Block C
- **230 V + Versorgung** unten (Reihe 3, Block B ganz rechts) — räumlich getrennt von SELV
- Kabel-Einführung von unten ins Gehäuse
- Tor-Kabel-Einführung von unten, kommt nahe Klemmenleiste in Reihe 2 rein

**Gesamt:** 24 TE belegt, **12 TE Reserve** → Erweiterungs-Reserve für Klingel, Lichtschranke, weitere Sensoren etc.

## 7. Verdrahtungs-Konvention

| Pfad | Querschnitt | Aderfarbe |
|---|---|---|
| 230 V → PSU | 1,5 mm² | L: schwarz, N: blau, PE: gn-ge |
| PSU → Sicherung → PTFIX | 0,5 mm² | rot (+24V), blau (GND) |
| PTFIX → RIF-0 Spule A1 (+24V) | 0,5 mm² | rot |
| RIF-0 → PTFIX GND | 0,5 mm² | blau |
| ESP-Relais (NO) → RIF-0 A1 (Spule) | 0,5 mm² | **= Funktionsfarbe des Kanals** (durchgängig BFT→Waveshare): R11 grau · R12 grün · R13 weiß · R14 gelb · R15/R16 rot (LED, +24-V-Antrieb). **Geändert 10-06-2026** — frühere „schwarz"-Festlegung verworfen (Schwarz = COM-Haupt, würde kollidieren). |
| RIF-0 K11/K14 ↔ Reihenklemme | 0,5 mm² | **= AHK-Funktionsfarbe** (durchgehende Codierung, geerntet aus AHK-Reststück — siehe `aderfarben_template.md`) |
| Reihenklemmen → AHK-Kabel → Tor | 0,5 mm² (AHK 13×0,5) | nach Aderfarbe (Belegung §6a / aderfarben_template.md) |

**Durchgängige Farbcodierung (bestätigt 03-06-2026):** Die Innenbrücken Reihenklemme↔RIF-0 werden in der **Funktionsfarbe** der jeweiligen AHK-Ader gezogen (aus dem entmantelten AHK-Reststück, ~3 m je Farbe übrig — reicht mit Faktor ~5). Versorgungs-/Sammelschienen (+24V rot, GND blau) bleiben in Standardfarbe aus den 6 separaten 20-AWG-Einzeladern. **Die ESP→Spule-Antriebe (NO→A1) laufen jedoch in der Funktionsfarbe des Kanals mit** (Entscheidung 10-06-2026, durchgängig BFT→Waveshare) — nur die 2 LED-Antriebe sind rot (kein BFT-Funktionskanal).

PTFIX Klemmbereich Eingang: 0,2–6 mm² → 0,5 mm² passt.
PT 2,5 Klemmbereich: 0,2–4 mm² eindrähtig → 0,5 mm² passt.
RIF-0 Push-in: 0,5 mm² mit Aderendhülse einschiebbar.

## 8. Open Points / Nächste Schritte

### Bestellungen / Aufbau / Test & Migration
> Bestellstatus siehe Tabelle oben (§ „Bestellstatus"); Aufbau-/Verdrahtungsstand + offene Anschlüsse siehe **§6a** (Innenausbau fertig + verifiziert 03-/10-06-2026, offen: PoE ans RJ45, Geräteseite Block C, Tor-Adern auf -U). Test & Migration: Parallel-Test mit temporärer 24-V-Quelle (ohne Bestand zu stören), dann Bestand abklemmen → neues System einklemmen.

### Software

**Plattform-Entscheidung:** **ESPHome** (vs Arduino SDK)
- Begründung: Alle bestehenden ESPs (Polar-Gateway, S400-Waage, LED-Matrix) laufen mit ESPHome → konsistenter Stack
- HA-Integration nativ (Discovery + API, Cover-Entity Standard-Component)
- Web-Interface via `web_server` Component
- OTA-Updates eingebaut
- Arduino SDK wäre nur sinnvoll bei sehr custom Hardware-Logik (Hochgeschwindigkeits-Timing, Bare-Metal) — hier nicht nötig

**Anforderungen Software:**
- [ ] **ESPHome YAML** für Waveshare schreiben
  - 6 switch (Öffnen (r1) / Schließen (r2) / Schritt (r3) / Fußgänger/Ped (r4) / LED blau (r5) / LED rot (r6))
  - 3 binary_sensor (Status Tor offen (DI1) / Status Tor zu (DI2) / externer Taster Dauerauf (DI3))
  - HA-Integration (cover.gate, sensor.gate_open, sensor.gate_closed, button.dauerauf)
  - **Web-Interface (web_server Component)** — für lokale Steuerung am Tor ohne HA-Abhängigkeit
  - **Einstellbare Parameter via `number` Component:**
    - Auto-Close-Zeit (Tor offen → schließen nach x Sekunden)
    - Close-bei-Unbekannt-Zeit (Tor hängt → Sicherheits-Close, Default 90s)
    - ggf. Impuls-Dauer, LED-Blink-Anzahl, etc.
  - **Auto-Close-Logik:**
    - **Standard Auto-Close**: Tor offen → nach x Sekunden Close-Befehl
    - **Notfall Auto-Close bei unbekanntem Status**: Wenn DI1=0 UND DI2=0 für länger als Schwelle (z.B. 90s), Close-Befehl. Verhindert dass Tor in Zwischenposition hängenbleibt. Default-Schwelle > typische Bewegungszeit + Puffer.
  - **Countdown-Sensor** als `sensor` (Restzeit in Sekunden) für **HA-Dashboard-Anzeige** (im ESP-Web nicht zwingend)
  - **Multi-HA-Zugriff (Mehrmandanten-Architektur):**
    - **Master:** **HA Keller/Hof** — bindet alle Hof-Geräte (Tore, Garagen, Außenbeleuchtung) direkt. ESP Hoftor wird hier eingebunden via ESPHome-Integration.
    - ⚠️ **Claude-Zugriff auf Keller = NUR LESEN** (Entscheidung 28-05-2026, siehe Memory `feedback_ha_instanzen_regeln.md`). Heißt: HA-seitige Einrichtung (Adoption, `cover.hoftor`, Dauerauf-/LED-Automationen, Labels/Area) macht **Florian selbst** im Keller-HA. **Claude liefert fertige Configs zum Einfügen, verifiziert lesend, dokumentiert.** Im DG-HA wird das Gerät NICHT adoptiert (keine Migration). ESP-YAML/OTA bleibt bei Claude (Builder/Repo, HA-unabhängig).
    - **Slaves:** HA Wohnung A + HA Wohnung B (Wohnungs-HAs) — spiegeln Hoftor-Entitäten via bestehender remote_homeassistant
    - **Privacy:** Wohnungs-HAs haben **keinen Zugriff untereinander**, nur lesend/schreibend auf gefilterten Master-Bestand
    - Filter pro Slave erweitern: `cover.hoftor*`, `switch.hoftor*`, `sensor.hoftor*`, `number.hoftor*`, `binary_sensor.hoftor*`
    - Nur 1 stabile API-Verbindung zum ESP → keine Restart-Storms
  - **ESPHome Stabilitäts-Settings:**
    - `api: reboot_timeout: 0s` (wichtig! verhindert Reboots bei HA-Disconnect)
    - `wifi/ethernet: reboot_timeout: 0s`
    - `logger: level: INFO`, api.connection auf WARN
    - encryption mit pre-shared key
- [ ] **Home Assistant Automationen**
  - Dauerauf-Logik: Taster gedrückt + Tor offen → Fußgänger/Ped (r4) dauerhaft halten bis erneut gedrückt oder Tor schließen-Befehl
  - LED-Blink-Logik: Wenn Dauerauf-Taster gedrückt aber Tor nicht offen → LED rot (r6) 5× blinken
  - Cover-Entity mit Position aus Status Tor offen (DI1) / Status Tor zu (DI2) ableiten

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
Trotz PSU mit Strombegrenzung wird eine **Glassicherung** (aktuell **2× 0,5 A flink** provisorisch; Soll: 0,5 A träge) in der **Phoenix PT 4-HESILED 24 Sicherungsklemme** zwischen PSU+ (27-O) und R-Block (27-U → R-a) eingesetzt. **1 A** passt zum 0,63-A-PSU (LED zeigt echten Fehler, nicht nur PSU-Strombegrenzung). Vorteil der HESI-Klemme: **LED zeigt durchgebrannte Sicherung an** — via **antiparallele LEDs**, daher **Einspeiseseite/Polarität egal** (Schaltplan 3211903 bestätigt). Service-Trennpunkt + Schutz + Sofort-Diagnose. **GND (0 V) wird NICHT abgesichert** (Rückleiter muss als Referenz durchverbunden bleiben).

### Netzwerk: Ethernet XOR WiFi (verifiziert 28-05-2026)
ESPHome erlaubt `ethernet:` und `wifi:` **nicht gleichzeitig** („may not be used simultaneously, even if both are physically available"). Kein Fallback-Netz möglich. Für dieses Projekt ist **Ethernet/PoE die richtige Wahl** (Grund für den Umbau war der schlechte WLAN-Empfang am Tor). Konsequenz: Ein „nach Flash nicht mehr pingbar" ist i. d. R. ein korruptes/abgebrochenes Image (z. B. PoE-Wackler beim OTA), KEIN fehlender Netzweg — ein WiFi-Fallback würde das auch nicht retten. **Recovery = USB-C-Reflash** (Configs sicher). Beim OTA die Versorgung stabil halten; `safe_mode` fängt nur fehlerhafte App-Logik ab, nicht ein totes Image.

## 10. Dateien & Referenzen

| Datei | Speicherort |
|---|---|
| Diese Doku | `S:\Projekte\hw-hoftor\CLAUDE.md` |
| **Firmware (ESPHome YAML)** | `S:\Projekte\hw-hoftor\hoftor.yaml` — Haupt-YAML, v0.40 |
| **Bedienungsanleitung** | `S:\Projekte\hw-hoftor\BEDIENUNG.md` — für Endbenutzer |
| Technische Doku Firmware (MD) | `S:\Projekte\hw-hoftor\Hoftor_Steuerung_Uebersicht.md` — Software/ESPHome-Logik |
| Technische Doku Firmware (Word) | `S:\Projekte\hw-hoftor\Hoftor_Dokumentation_v0.39.docx` — menschenlesbare Kopie der .md |
| **Verdrahtungs-Doku (MD)** | `S:\Projekte\hw-hoftor\Hoftor_Verdrahtung_v1.md` — Hardware/Belegungsplan (SSoT) |
| **Verdrahtungs-Doku (Word)** | `S:\Projekte\hw-hoftor\Hoftor_Verdrahtung_v1.docx` — menschenlesbare Kopie der .md |
| **AHK-Klemmenplan (Druckvorlage)** | `S:\Projekte\hw-hoftor\Hoftor_AHK_Klemmenplan.html` — UV↔BFT Aderfarben, druckbar |
| Kurzbeschreibung Web-Interface | `S:\Projekte\hw-hoftor\Hoftor_Kurzbeschreibung_Webinterface.md` |
| Web-UI Bedien-Anleitung (JS-Inject) | `S:\Projekte\hw-hoftor\hoftor_help.js` |
| Web-UI LCARS-Theme (CSS) | `S:\Projekte\hw-hoftor\hoftor_lcars.css` |
| Aderfarben-Template | `S:\Projekte\hw-hoftor\aderfarben_template.md` |
| **Test-/Inbetriebnahme-Checkliste** | `S:\Projekte\hw-hoftor\Hoftor_Testplan.md` — Stufe 1 (ohne 24 V) + Stufe-2-Vorschau |
| **Funk-Empfänger Hörmann (Übergabe)** | `S:\Projekte\hw-hoftor\Hoftor_Hoermann_Funkempfaenger_Uebergabe.md` — HET/S 24, DI7/DI8, Verdrahtung + HA-Plan |
| BFT Thalia Handbuch (im Repo) | `S:\Projekte\hw-hoftor\THALIA_DUO_BT_A80_A160.pdf` |

### Shops/Bezugsquellen
- **automation24.de** — Phoenix-Klemmen, Koppelrelais, PTFIX, FIBOX-Verteiler (alles 1× verfügbar, keine Großpackungen)
- **Amazon** — PT 2,5-TWIN 3-polig (Phoenix-Äquivalent oder Drittanbieter)
- **Waveshare-Shop / Amazon / AliExpress** — ESP32-S3-POE-ETH-8DI-8RO
- **Conrad/Reichelt/Baumarkt** — Glassicherungen 1 A T 5×20

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

## Normen-Hinweis (Aderfarben N vs DC-GND)

In dieser Anlage existieren **N (230V Neutralleiter)** und **DC-GND (24V SELV-Masse)** parallel — beide werden umgangssprachlich "blau" genannt.

**Pragmatische Lösung gewählt** (für private Anlage ausreichend):
- Räumliche Trennung: **230V komplett in Reihe 3**, **24V SELV in Reihe 2** + ESP in Reihe 1
- **Beschriftung an den Hutschienen**:
  - Reihe 3: Aufkleber/Schild **"230 V AC"**
  - Reihe 2: Aufkleber/Schild **"24 V DC SELV"**
- ZB 5 Klemmen-Beschriftung: "L", "N", "PE" für 230V; "+24V", "0V/GND" für DC
- Auf Verteiler-Innentür: Hinweis "230V und 24V im selben Gehäuse — siehe Beschriftung"

Norm-strikte Alternative (nicht umgesetzt): DC-GND-Adern + Klemmen in dunkelblau oder weiß/schwarz statt hellblau. Bei Bedarf nachrüstbar.

## Bei nächster Session

Diese Datei lesen für vollen Kontext.

**Nächste konkrete Schritte (Priorität):**
1. **Waveshare ESP32-S3-POE-ETH-8DI-8RO bestellen** (Waveshare-Shop, AliExpress oder Amazon)
2. **Anhängerkabel 13×0,5 mm² (5 m)** bei Amazon bestellen
3. Bei Wareneingang der automation24- und Amazon-Sendung: **Aufbau im FIBOX-Verteiler** nach Layout
4. Sobald Anhängerkabel da: **Aderfarben festlegen** und in CLAUDE.md ergänzen
5. **ESPHome-YAML** schreiben sobald ESP da
6. **HA-Automationen** (Cover-Entity, Dauerauf-Logik, LED-Blink) parallel zur Software-Inbetriebnahme

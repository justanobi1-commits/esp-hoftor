# Hoftor-Steuerung — Gesamtübersicht

> **Zweck dieser Datei:** (A) Ein anderer Claude versteht damit die Steuerung ohne die ganze Projekthistorie. (B) Sie erklärt einem Menschen, wie das Tor bedient wird.
> **Stand:** 19-06-2026 · Firmware `hoftor.yaml` **v0.39** · ESP `192.168.200.40` (Ethernet/PoE)
> **Tiefe Details:** `CLAUDE.md` (Volldoku) · `aderfarben_template.md` (Verdrahtung) · `Hoftor_AHK_Klemmenplan.html` (Auflegeplan) · `Hoftor_Hoermann_Funkempfaenger_Uebergabe.md` (Funk)

---

# TEIL A — Briefing für Claude

## Was ist das?
Ein **Waveshare ESP32-S3-POE-ETH-8DI-8RO** (ESPHome) steuert eine **BFT Thalia BT A80/A160 + EBD**-Hoftoranlage. Er ersetzt 3× Shelly Uni Plus (schlechter WLAN-Empfang → jetzt PoE). Der ESP gibt **nur Impulse/Haltesignale** an die BFT; die eigentliche Motorsteuerung macht die BFT. **Der ESP sieht keine Funk-Handsender-Befehle** — den Tor-Zustand erfährt er nur über die Status-DIs.

## Signalkette (wichtig!)
```
ESP-Relais (PCA9554) → Onboard-Relais CHx → Phoenix RIF-0 Koppelrelais (Pos. 11–20) → Reihenklemme 1–10 → AHK-Kabel → BFT-Klemme
```
Jedes Feld-I/O läuft über ein RIF-0 (galvanische Trennung innen↔außen). Klemmen-Ebenen: **-O = innen/Relais**, **-U = außen/Tor**.

## Kanäle & Pins (`hoftor.yaml`)
| ESP | PCA-Pin / CH | Funktion | → BFT | Hinweis |
|---|---|---|---|---|
| r1 | Pin 0 / CH1 | **Öffnen** (Impuls), gehalten = Dauerauf | 65 (Open, IC=2) | |
| r2 | **Pin 6 / CH7** | **Schließen** (Impuls) | 62 (Close, IC=3) | v0.38 von CH2 umgeklemmt |
| r3 | Pin 2 / CH3 | **Schritt** (auf-stopp-zu) | 64 (Start E, IC=0) | |
| r4 | Pin 3 / CH4 | **Fußgänger/Ped**, gehalten = Ped-Dauerauf | 61 (Timer Ped, **IC=6**) | |
| r5 | Pin 4 / CH5 | LED blau (Tor offen) | — | |
| r6 | Pin 5 / CH6 | LED rot (Halten aktiv) | — | |

**DIs** (GPIO4–11, INPUT_PULLUP, inverted; aktiv = +24 V über RIF-0):
- **DI1** = Status Tor offen (BFT 24) · **DI2** = Status Tor zu (BFT 26) · **DI3** = externer Taster Dauerauf
- **DI7** = Funk Hörmann K1 · **DI8** = Funk Hörmann K2 · DI4–DI6 = Reserve

## ⚠️ Fallen, die ein Claude kennen muss
1. **61 = Ped (IC=6), 65 = Open (IC=2)** — *nicht* vertauschen. Bei falscher BFT-Parametrierung lösen „Öffnen" (Ch1→65) und „Fußgänger" (Ch4→61) vertauscht aus (auch Funk K1). → ToDo **HT-BFT**.
2. **r2 sitzt auf CH7/Pin 6** (umgeklemmt). War eine Fehldiagnose („HW-Boot-Glitch"); echte Ursache war Software (siehe Punkt 3). Umklemmung bleibt, schadet nicht.
3. **Boot-Close-Bug (v0.39 gefixt):** `dauerauf`/`ped_halten` sind template-Switches mit Default `restore_mode: ALWAYS_OFF`, der beim Boot `turn_off_action` → `hold_close` → `pulse_close` (r2) auslöste. Fix: **`restore_mode: DISABLED`** an beiden. Lehre: template-Switch mit gefährlicher `turn_off_action` braucht `DISABLED`.
4. **Störungs-Erkennung:** Wenn DI1=DI2=0 (kein Endschalter) für >180 s → ESP sendet `pulse_close` (bis 3×, dann Esk2-Alarm). Bei nicht angeschlossener BFT ein Fehlalarm → im Bench-Test `Test: DI2 Tor zu` setzen.
5. **Repo `esp-hoftor` ist PUBLIC** → niemals Secrets (OTA-PW, api_key) in die YAML committen. Secrets liegen in der `secrets.yaml` der ESPHome-Instanz.
6. **Server-Sync:** ESPHome baut aus `\\192.168.210.11\config\esphome\hoftor.yaml`, **nicht** aus dem Repo. Bei YAML-Änderung: Repo editieren **+** auf Server kopieren + SHA256 gegenprüfen.
7. **Keller-HA = read-only für Claude** — HA-Automationen/Entities macht Florian selbst (Claude liefert nur Configs).

## Firmware-Logik (Kurzform)
- **Buttons** = fixer 1-s-Impuls (`pulse_open/close/step/ped`).
- **Dauerauf** (hält r1) / **Fußgänger-Dauerauf** (hält r4): gegenseitig verriegelt; AUS → nach 1 s Close (`hold_close`).
- **Auto-Close** je Ch1/Ch4 (0 = aus), Trigger = DI1 (funktioniert auch bei Funk-Öffnung).
- **Störungs-Erkennung** + **Close-Reaktions-Check** (Esk1/Esk2, `device_class: problem` für HA-Push).
- **LEDs:** blau = DI1 (Tor offen); rot = Dauerauf||Ped-Halten. `blink_rot_5x` bei Taster-Verweigerung.
- **web_server v3** (LCARS-CSS, Live-Log, Bedien-Anleitung via `js_include`). ⚠️ Offener Browser-Tab streamt dauernd → bremst OTA/erhöht Latenz.

## Hörmann-Funk (reine Melder)
**HET/S 24 BiSecur**, 24 V (über Sicherung 28), 2 potenzialfreie Relais → +24 V auf **DI7 (K1)/DI8 (K2)**. Bewusst **ohne `on_press`** — der ESP meldet nur (`binary_sensor.hoftor_funk_hormann_k1` / `_k2`); **was die Kanäle auslösen, wird frei in HA festgelegt** und ist ohne Re-Flash änderbar.

## HA-Anbindung
- **Master = Keller-HA** (`home-assistant-keller`, deckt Keller/Hof). ESP dort adoptiert.
- Geplant: `cover.hoftor`, Dauerauf-/LED-Automationen, Funk-K1/K2-Automationen. **Macht Florian** (Claude read-only).

## Aktueller Stand (19-06-2026)
- ✅ Verteiler/ESP-Seite fertig + im **Bench-Test** (Relais/DI ohne Tor). v0.39 geflasht, Repo↔Server synchron.
- ✅ AHK-Adern auf **UV-Klemmen 1–10 (-U)** aufgelegt (Farben bestätigt). Hörmann verdrahtet.
- ⏳ **Offen:** BFT-/Tor-Seite der AHK-Adern auflegen (Enden in Berührungsschutz-WAGOs) · Block-C-Geräteseite · BFT-Parametrierung · Live-Test (inkl. **Ped-Verhalten: was sendet Open/Close bei aktivem Fußgänger-Modus?**) · HA-Automationen · Migration (3× Shelly raus) · Sicherungen 0,5 A **träge** + Endkappe `D-ST 4`.

---

# TEIL B — Bedienung für den Menschen

Das Tor lässt sich auf **vier Wegen** bedienen: Web-Seite, Home Assistant, Funk-Handsender, Taster vor Ort.

## 1. Web-Seite (lokal, ohne HA)
**`http://192.168.200.40`** im Browser (LCARS-Optik). Gruppen:
- **Ch1 – Tor auf:** `Öffnen` (Impuls) · `Dauerauf` (Tor bleibt offen, bis wieder aus)
- **Ch2 – Tor zu:** `Schließen`
- **Ch3 – auf-stopp-zu:** ein Impuls = nächster Schritt der Tor-Bewegung
- **Ch4 – Fußgänger:** `Fußgänger` (nur ein Flügel/Teilöffnung) · `Fußgänger Dauerauf`
- **Eingänge:** zeigt Status *Tor offen / Tor zu*, Taster, Funk K1/K2
- **Störungs-Erkennung / Diagnose / Test:** Restzeiten, Verbindung, Test-Schalter

Über dem Live-Log steht eine **eingebaute Kurz-Anleitung**.

## 2. Home Assistant
Im **Keller-HA** erscheinen die Tor-Funktionen als Schalter/Buttons (später als `cover.hoftor`). Von dort auch per Sprachassistent/Automationen bedienbar.

## 3. Funk-Handsender (Hörmann BiSecur)
- Jede Handsender-Taste meldet sich als Eingang am ESP: **K1 → DI7**, **K2 → DI8**.
- **Was die Tasten auslösen, wird in Home Assistant festgelegt** (frei änderbar, ohne den ESP neu zu flashen).
*(Der Handsender spricht den Funk-Empfänger an, der meldet's an den ESP/HA.)*

## 4. Taster vor Ort
Ein Taster am Schuppen schaltet **Dauerauf** — aber aus Sicherheit **nur, wenn das Tor bereits offen ist**. Ist es zu, blinkt die rote LED 5× (keine Aktion). Der Taster kann das Tor also nie selbst öffnen.

## Was bedeuten die Begriffe?
| Begriff | Bedeutung |
|---|---|
| **Öffnen / Schließen** | Kurzer Impuls — Tor fährt ganz auf bzw. zu |
| **Schritt (auf-stopp-zu)** | Ein Druck = nächster Schritt (auf → stopp → zu → …) |
| **Dauerauf** | Tor bleibt dauerhaft offen, bis du es wieder ausschaltest (dann schließt es nach 1 s) |
| **Fußgänger** | Nur ein Flügel / Teilöffnung zum Durchgehen |
| **Auto-Schließen** | Optionale Zeit — Tor schließt von selbst x Sekunden nach dem Öffnen (0 = aus) |

## Die zwei LEDs
- **Blau** leuchtet, wenn das **Tor offen** ist.
- **Rot** leuchtet, wenn ein **Halten** aktiv ist (Dauerauf oder Fußgänger-Dauerauf). 5× kurzes Blinken = ein Befehl wurde verweigert.

## Störung
Hängt das Tor länger als ~3 Minuten in einer Zwischenstellung (weder ganz auf noch ganz zu), versucht die Steuerung automatisch zu schließen und meldet bei wiederholtem Fehlschlag eine **Störung** an Home Assistant (Push/Benachrichtigung). Die eigentliche Alarmierung übernimmt HA.

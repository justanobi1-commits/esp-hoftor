# Übergabe: Hörmann Funk-Empfänger fürs Hoftor (HET/S 24 BiSecur)

> **Kontext-Übergabe aus einer anderen Claude-Session — Stand 19-06-2026.**
> **Zuerst lesen:** `S:\Projekte\hw-hoftor\CLAUDE.md` + `hoftor.yaml` (voller Projektkontext).
> Dieses Dokument ergänzt **nur den Hörmann-Funkempfänger-Teil**, der in der CLAUDE.md noch nicht steht.
>
> **🔄 UPDATE 19-06-2026:** Empfänger **real an DI7/DI8** verkabelt (nicht DI4/DI5 wie unten ursprünglich geplant) →
> `hoftor.yaml` **v0.39** im Repo (kein Server-Sync — Hoftor gehört zur Keller-HA, nicht DG), geflasht 19-06.
> Abschnitte „Verdrahtung", „Bereits erledigt" und „Offene Punkte" sind unten entsprechend aktualisiert.

## Ziel
Mit einem **Hörmann-BiSecur-Handsender** sollen über einen Funkempfänger Funktionen in HA ausgelöst werden:
- **Kanal 1 (K1) → Hoftor öffnen (Impuls)**
- **Kanal 2 (K2) → evtl. Hoflicht (Shelly)**

Der Empfänger liefert pro Tastendruck einen **potenzialfreien Relaiskontakt**, der an einen freien DI der vorhandenen Waveshare-Steuerung geht. Die eigentliche Schalt-Logik liegt **in HA** (so lässt sich die Funktion später ohne Re-Flash umlegen).

## Produkt (recherchiert + bestätigt)
**Hörmann HET/S 24 868-BS** — 2-Kanal-Relais-Empfänger, BiSecur (868 MHz):
- 2× **potenzialfreie** Relais, je **Impuls (0,5 s)** oder Dauer (Ein/Aus) wählbar
- Versorgung **12–24 V DC** (NICHT 230 V; kein eigenes Netzteil)
- ausdrücklich **„auch für Fremdhersteller"** (fremde Impulseingänge)
- nur **868-MHz-BiSecur**-Handsender, **nicht** Festcode

Alternativen:
- **HET/S 2 868-BS** — gleicher Empfänger, aber mit **Steckernetzteil** (für reine 230-V-Steckdose ohne 24-V-Quelle)
- **HER 1 / 2 / 4 BS** — Externempfänger 1/2/4-Kanal, potenzialfrei, IP65 (auch außen)
- **ESE BS** — 5-Kanal bidirektional (Rückmeldung) → **nicht** für simples Impuls-Schalten geeignet

## Hardware-Kontext (Details: CLAUDE.md §4–6a)
- Steuerung: **Waveshare ESP32-S3-POE-ETH-8DI-8RO**, FIBOX MCE65, ESPHome, **PoE**, IP **192.168.200.40**
- **24 V DC im Schrank** vorhanden (Phoenix STEP POWER 1088495, 0,63 A; Reserve reicht, Empfänger zieht ~mA)
- DIs = **opto-isolierte 24-V-Industrieeingänge**, **DI-COM liegt auf GND** → Aktiv-Pegel = **+24 V auf den DI**
- Belegt: DI1=Status offen, DI2=Status zu, DI3=Taster, **DI7=Funk K1 / DI8=Funk K2** (real verkabelt 19-06). Frei: DI4–DI6 (GPIO7–GPIO9)

## Verdrahtung
```
24V+ (R-Block) ──▶ HET/S 24  V+        (12–24 V → 24 V passt)
24V- (Bl-Block)──▶ HET/S 24  V-

Kanal 1:  +24V (R-Block) ──▶ Relais COM
          Relais NO       ──▶ DI7-Klemme   (real K1, grün)
Kanal 2:  +24V            ──▶ Relais COM
          Relais NO       ──▶ DI8-Klemme   (real K2, gelb)
          (DI-COM liegt bereits auf GND)
```
- Handsender → Relais 0,5 s → +24 V auf DI → DI meldet aktiv
- **Elektrisch identisch zum bestehenden F3/F4-Status-Schema** (RIF-0 schaltet +24 V auf DI1/DI2)
- **Kein extra Koppelrelais nötig** (Empfänger sitzt im Schrank, Kontakt schon potenzialfrei, DI opto-isoliert)
- ESP bleibt auf **PoE** (VIN frei) → kein PoE/VIN-Konflikt
- Empfänger-Kanäle auf **Impuls (0,5 s)** stellen

## Bereits erledigt (ESP-Repo)
- `hoftor.yaml` **v0.37** (19-06-2026): Funk Hörmann K1/K2 auf **DI7/DI8** (GPIO10/GPIO11) — real so verkabelt.
  (v0.36 plante DI4/DI5; diese sind jetzt wieder generische Reserve, ebenso DI6.)
  - reine Melder (binary_sensor, `INPUT_PULLUP, inverted`, Entprellung 20/50 ms)
  - **bewusst kein `on_press`** → Schalt-Logik liegt in HA
  - HA-Entities nach Flash: `binary_sensor.hoftor_funk_hormann_k1` / `_k2`
- **Repo + Server synchron auf v0.37** (SHA256 byte-identisch); Stände v0.35/v0.36 in `archive/`.
- **Noch offen:** v0.37 flashen (ESP läuft noch auf älterem Stand); CLAUDE.md §5/§6a + Versionsstand nachziehen

## HA-Belegung (von FLORIAN umzusetzen — NICHT von Claude, siehe Regeln)
- **K1 → Hoftor (Impuls):** Automation auf `binary_sensor.hoftor_funk_hormann_k1` → `button.hoftor_ch1_offnen` (Ch1 Öffnen). *(Hoftor hat noch keine `cover`-Entity.)*
- **K2 → evtl. Hoflicht (Shelly):** Automation → Hoflicht-Shelly-Entity (ID noch ermitteln)
- Instanz: **Keller-HA** (`home-assistant-keller`, deckt Keller/Gemeinschaft/Hof)
- Vorhandene Hoftor-Entities (Keller): `button.hoftor_ch1_offnen` / `ch2_schliessen` / `ch3_auf_stopp_zu` / `ch4_fussganger`; DIs `binary_sensor.hoftor_di4 … di8` (→ `funk_hormann_k1/_k2` nach Flash)
- ⚠️ Garagentore (`cover.*hcpbridge*`) waren ein Irrweg meinerseits → **verworfen, NICHT Ziel**

## VERBINDLICHE REGELN
- **HA-Instanz Keller/Gemeinschaft/Hof (`home-assistant-keller`): Claude fasst dort NICHTS an.** Keine Automationen/Entities/Helfer/Skripte/Dashboards/Config; nichts via HA-MCP pushen. **Nur lesen** zum Beraten. **Florian setzt alle HA-Änderungen selbst um** (YAML/Schritte liefern, nicht deployen).
- **Projekt-/ESP-Repos** unter `S:\Projekte\…` darf Claude bearbeiten.
- **Arbeitspfad/Memory = S:\** (TrueNAS `\\192.168.202.10\claude`). **NIE** nach `C:\Users\obero\OneDrive\` schreiben (tot/archiviert).

## Offene Punkte
1. ~~HET/S 24 bestellen + verdrahten~~ ✅ **verdrahtet 19-06-2026** (COM=+24 V über Sicherung 28, NO=DI7/DI8)
2. **ESP v0.37 OTA flashen** + DI7/DI8 (Funk K1/K2) testen — Florian
3. **CLAUDE.md auf v0.37 nachziehen** (DI-Tabellen §5/§6a + Sicherung 28 belegt + Status)
4. **HA-Automationen** K1 (Hoftor öffnen) + K2 (Hoflicht) — Florian
5. **Hoflicht-Shelly-Entity-ID** ermitteln (für K2)

## Quellen (Produkt)
- HET/S 24: https://www.tor7.de/hoermann-2-kanal-relais-empfaenger-het-s-24-bisecur
- HET/S 2: https://www.tor7.de/hoermann-2-kanal-relais-empfaenger-het-s-2-bisecur
- HET-E2 (bidirektional): https://www.tor7.de/hoermann-2-kanal-relais-empfaenger-het-e2-bisecur-bidirektional
- HER 1: https://www.tor7.de/hoermann-1-kanal-relais-empfaenger-her-1-bisecur
- Versorgung 12–24 V DC bestätigt: https://www.garagentor-ersatzteile.de/garagentorantriebe-hoermann/funk-empfaenger/empfaenger-hoermann-het_s-24-bs-2-kanal-8683-mhz-bisecur

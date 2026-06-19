# Aderfarben-Belegung Hoftor

## Konzept

**Durchgehende Farbcodierung** vom BFT-Klemmenanschluss bis zur Phoenix RIF-0 Spule/Kontakt. Eine Farbe = eine Funktion. Der Außenmantel des 5 m Anhängerkabels wird nur im Leerrohr (< 1 m Tor↔Verteiler) genutzt — die restlichen ~4 m werden im Verteiler **entmantelt** und die Einzeladern bis zum Relais weitergeführt.

## Tatsächlich vorhandene Adern

**AHK-Kabel (Anhängerkabel) — 13 Adern, alle 0,5 mm²**, Strecke Tor ↔ Verteiler (Klemmen 1–10), 5 m lang. Mantel nur im Leerrohr, Rest entmantelt als Einzelader weiter:

`Blau` · `Gelb` · `Grau` · `Weiß-Blau` · `Rot` · `Rosa` · `Weiß-Schwarz` · `Schwarz` · `Orange` · `Braun` · `Weiß-Rot` · `Grün` · `Weiß`

(13 eindeutige Farben — „2. Rot" war Orange.)

**Einzeladern 20 AWG (≈0,5 mm²)** als Vorrat für Innenverdrahtung im Verteiler:

`Gelb` · `Schwarz` · `Grün` · `Blau` · `Weiß` · `Rot`

→ Das AHK-Kabel kann bei Bedarf zusätzlich entmantelt werden, um weitere Einzeladern zu gewinnen.

## Zuordnungstabelle

„Geht zu" mit physischer Relais-Nummerierung (11–20), F-Rolle in Klammern (= ESPHome-Bezug).

| PT-Klemme# | BFT-Klemme | Aderfarbe | Funktion | Geht im Verteiler zu |
|---|---|---|---|---|
| 1 (TWIN) | 60 | **Schwarz** | COM Hauptplatine | Relais 12 (F2)-K14 + Relais 14 (F6)-K14 (via TWIN) |
| 2 | 61 | **Gelb** | Ped / Fußgänger (Ch4) | Relais 14 (F6)-K11 |
| 3 | 62 | **Grün** | Close | Relais 12 (F2)-K11 |
| 4 (TWIN) | 63 | **Braun** | COM EBD | Relais 11 (F1)-K14 + Relais 13 (F5)-K14 (via TWIN) |
| 5 | 64 | **Weiß** | Start E (Schritt) | Relais 13 (F5)-K11 |
| 6 | 65 | **Grau** | Öffnen (Ch1) | Relais 11 (F1)-K11 |
| 7 | 24 | **Rot** | Status Tor offen — Signal | Relais 17 (F3)-A1 |
| 8 | 26 | **Rosa** | Status Tor zu — Signal | Relais 18 (F4)-A1 |
| 9 | 25 | **Blau** | Status offen — Rückleiter (**+24V**) | R-Block via FBS 2-5 rot (Klemme 9↔10) |
| 10 | 27 | **Weiß-Blau** | Status zu — Rückleiter (**+24V**) | R-Block via FBS 2-5 rot (Klemme 9↔10) |
| 11–13 (Reserve) | – | Weiß-Schwarz · Weiß-Rot · Orange ⚠️ | (Reserve) | – |

⚠️ **Orange meiden:** ähnelt zu sehr der roten Einzelader → Verwechslungsgefahr. Orange bleibt möglichst unbenutzt; bei Reserve-Bedarf Weiß-Schwarz / Weiß-Rot bevorzugen.

**Begründung der Gruppierung:** COMs dunkel/neutral (Schwarz/Braun) · 4 Impuls-Befehle hell/auffällig (Gelb/Grün/Weiß/Grau) · 2 Status-Signale warm (Rot/Rosa) · 2 +24V-Rückleiter blau-Töne (Blau/Weiß-Blau, passen zusammen, da per FBS-Brücker verbunden).

## ESP-Seite — Innenverdrahtung Waveshare

**Prinzip: Funktionsfarbe durchgängig bis zum Waveshare.** Die Spulen-Antriebe (Onboard-Relais NO → RIF-0 A1) und die DI-Signale (RIF-0 K14 → ESP-DI) laufen in der **Funktionsfarbe des jeweiligen Kanals** weiter — *nicht* schwarz. So ist jeder Kanal von der BFT-Klemme bis zum ESP eine Farbe. Versorgung bleibt rot (+24 V) / blau (GND).

| ESP-Verbindung | Farbe | Funktion |
|---|---|---|
| R-Block → Relais-COMs | **Rot** | +24-V-Einspeisung (CH1←R-c · CH3←R-g · CH4←R-i · CH5←R-k · CH6←R-m · **CH7←neu, Schließen seit v0.38**). CH2 unbenutzt (war R-e). |
| CH1-NO → R11-A1 | **Grau** | Öffnen (= Kl. 6 / BFT65) |
| **CH7**-NO → R12-A1 | **Grün** | Schließen (= Kl. 3 / BFT62) — v0.38 von CH2 umgeklemmt (CH2-Boot-Glitch) |
| CH3-NO → R13-A1 | **Weiß** | Schritt (= Kl. 5 / BFT64) |
| CH4-NO → R14-A1 | **Gelb** | Dauerauf/Ped (= Kl. 2 / BFT61) |
| CH5-NO → R15-A1 | **Rot** | LED blau (kein BFT-Kanal → +24-V-Antrieb = rot) |
| CH6-NO → R16-A1 | **Rot** | LED rot (kein BFT-Kanal → +24-V-Antrieb = rot) |
| R17-K14 → DI1 | **Rot** | Status Tor offen (= Kl. 7 / BFT24) — *offen, noch zu verdrahten* |
| R18-K14 → DI2 | **Rosa** | Status Tor zu (= Kl. 8 / BFT26) — *offen* |
| R19-K14 → DI3 | **Weiß-Schwarz** | Taster (= Kl. 26) — *offen* |
| Bl-Block → DI-COM | **Blau** | GND-Referenz der DIs — *offen; COM vs. DGND am Header noch klären* |

⚠️ **Schwarz ist NICHT der Antrieb** (frühere Annahme verworfen): Schwarz = COM-Hauptplatine (BFT60, Kl. 1). Antriebe tragen die Kanal-Funktionsfarbe.

## Beschriftung der Reihenklemmen

Zusätzlich zum Phoenix ZB 5 Beschriftungsstreifen (Zahlen 1-10) kann man mit Filzstift unter jede Klemmennummer die **Aderfarbe** notieren:

```
┌─────────┐
│   #1    │
│  TWIN   │
│ BFT 60  │
│ schwarz │  ← Aderfarbe mit Filzstift
│ COM Hpt │
└─────────┘
```

Oder kleine **farbige Punkt-Sticker** auf den ZB-Streifen kleben.

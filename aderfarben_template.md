# Aderfarben-Belegung Hoftor

**Version:** 1.3
**Stand:** 03-06-2026
**Status:** Adern vorhanden + dokumentiert. Reihenfolge Klemmen 1–10 + Farb-Mapping **bestätigt 03-06-2026**. Verdrahtung noch offen (AHK-Adern noch nicht aufgelegt).

## Konzept

**Durchgehende Farbcodierung** vom BFT-Klemmenanschluss bis zur Phoenix RIF-0 Spule/Kontakt. Eine Farbe = eine Funktion. Der Außenmantel des 5 m Anhängerkabels wird nur im Leerrohr (< 1 m Tor↔Verteiler) genutzt — die restlichen ~4 m werden im Verteiler **entmantelt** und die Einzeladern bis zum Relais weitergeführt.

## Tatsächlich vorhandene Adern (Stand 03-06-2026)

**AHK-Kabel (Anhängerkabel) — 13 Adern, alle 0,5 mm²**, Strecke Tor ↔ Verteiler (Klemmen 1–10), 5 m lang. Mantel nur im Leerrohr, Rest entmantelt als Einzelader weiter:

`Blau` · `Gelb` · `Grau` · `Weiß-Blau` · `Rot` · `Rosa` · `Weiß-Schwarz` · `Schwarz` · `Orange` · `Braun` · `Weiß-Rot` · `Grün` · `Weiß`

(13 eindeutige Farben — „2. Rot" war Orange, korrigiert 03-06.)

**Einzeladern 20 AWG (≈0,5 mm²)** als Vorrat für Innenverdrahtung im Verteiler:

`Gelb` · `Schwarz` · `Grün` · `Blau` · `Weiß` · `Rot`

→ Das AHK-Kabel kann bei Bedarf zusätzlich entmantelt werden, um weitere Einzeladern zu gewinnen.

## Zuordnungstabelle — bestätigt 03-06-2026

Reihenfolge Klemmen 1–10 + Farben bestätigt. „Geht zu" mit neuer physischer Relais-Nummerierung (11–20), F-Rolle in Klammern (= ESPHome-/Schaltplan-Bezug).

| PT-Klemme# | BFT-Klemme | Aderfarbe | Funktion | Geht im Verteiler zu |
|---|---|---|---|---|
| 1 (TWIN) | 60 | **Schwarz** | COM Hauptplatine | Relais 12 (F2)-K14 + Relais 14 (F6)-K14 (via TWIN) |
| 2 | 61 | **Gelb** | Open (Dauerauf) | Relais 14 (F6)-K11 |
| 3 | 62 | **Grün** | Close | Relais 12 (F2)-K11 |
| 4 (TWIN) | 63 | **Braun** | COM EBD | Relais 11 (F1)-K14 + Relais 13 (F5)-K14 (via TWIN) |
| 5 | 64 | **Weiß** | Start E (Schritt) | Relais 13 (F5)-K11 |
| 6 | 65 | **Grau** | Open (Impuls) | Relais 11 (F1)-K11 |
| 7 | 24 | **Rot** | Status Tor offen — Signal | Relais 17 (F3)-A1 |
| 8 | 26 | **Rosa** | Status Tor zu — Signal | Relais 18 (F4)-A1 |
| 9 | 25 | **Blau** | Status offen — Rückleiter (**+24V**) | R-Block via FBS 2-5 rot (Klemme 9↔10) |
| 10 | 27 | **Weiß-Blau** | Status zu — Rückleiter (**+24V**) | R-Block via FBS 2-5 rot (Klemme 9↔10) |
| 11–13 (Reserve) | – | Weiß-Schwarz · Weiß-Rot · Orange | (Reserve) | – |

**Begründung der Gruppierung:** COMs dunkel/neutral (Schwarz/Braun) · 4 Impuls-Befehle hell/auffällig (Gelb/Grün/Weiß/Grau) · 2 Status-Signale warm (Rot/Rosa) · 2 +24V-Rückleiter blau-Töne (Blau/Weiß-Blau, passen zusammen, da per FBS-Brücker verbunden).

## Bei Wareneingang ausfüllen

1. **Foto aller 13 Adern** beim Auspacken
2. **Liste der Aderfarben** vom Hersteller/Verpackung (oft beigelegt)
3. **Farben zu Funktionen** zuordnen — Tipp: ähnliche Funktionen ähnliche Farb-Gruppen geben
4. **Diese Datei aktualisieren** mit den eingetragenen Farben
5. **CLAUDE.md ergänzen** mit fertiger Zuordnung

## Empfehlung für die Zuordnungslogik

Sinnvoll: Adern nach Funktion gruppieren (visuelle Diagnose):

| Gruppe | Adern | Empfehlung Farb-Familie |
|---|---|---|
| COMs (1, 4) | 2× | dunkle/neutrale Farben (schwarz, braun) |
| Befehle Impuls (2, 3, 5, 6) | 4× | helle/auffällige Farben (gelb, grün, weiß, orange) |
| Status-Signale (7, 8) | 2× | warme Farben (rot, rosa) |
| Status-GND (9, 10) | 2× | blau-Töne |
| Reserve (11–13) | 3× | bleiben unbeschaltet, beliebige Farbe |

→ Diese Zuordnung ist nur eine Empfehlung. Bei der Lieferung kann sich aus den tatsächlich vorhandenen Farben eine andere Logik ergeben.

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

## Stand

- [x] Kabel bestellt
- [x] Kabel geliefert (AHK-Kabel vorhanden)
- [x] Farben dokumentiert (03-06-2026)
- [x] Tabelle oben ausgefüllt + bestätigt (03-06-2026)
- [x] CLAUDE.md aktualisiert (Belegungsplan §6a, 03-06-2026)
- [ ] AHK-Adern am Tor + an Klemmen 1–10 auflegen
- [ ] Verteiler-Innenseite mit Aderfarben-Karte beklebt

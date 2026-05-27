# Aderfarben-Belegung Hoftor — Template

**Version:** 1.1
**Stand:** 27-05-2026
**Status:** Template — bei Eintreffen des ETUKER Anhängerkabels (Freitag 29-05-2026) mit tatsächlichen Farben füllen

## Konzept

**Durchgehende Farbcodierung** vom BFT-Klemmenanschluss bis zur Phoenix RIF-0 Spule/Kontakt. Eine Farbe = eine Funktion. Der Außenmantel des 5 m Anhängerkabels wird nur im Leerrohr (< 1 m Tor↔Verteiler) genutzt — die restlichen ~4 m werden im Verteiler **entmantelt** und die Einzeladern bis zum Relais weitergeführt.

## Zuordnungstabelle (zu vervollständigen)

| PT-Klemme# | BFT-Klemme | Aderfarbe | Funktion | Geht im Verteiler zu |
|---|---|---|---|---|
| 1 (TWIN) | 60 | ___________ | COM Hauptplatine | F2-K14 + F6-K14 (via TWIN-Klemme) |
| 2 | 61 | ___________ | Open (Dauerauf) | F6-K11 |
| 3 | 62 | ___________ | Close | F2-K11 |
| 4 (TWIN) | 63 | ___________ | COM EBD | F1-K14 + F5-K14 (via TWIN-Klemme) |
| 5 | 64 | ___________ | Start E (Schritt) | F5-K11 |
| 6 | 65 | ___________ | Open (Impuls) | F1-K11 |
| 7 | 24 | ___________ | Status Tor offen — Signal | F3-A1 |
| 8 | 26 | ___________ | Status Tor zu — Signal | F4-A1 |
| 9 | 25 | ___________ | Status offen — Rückleiter (**+24V**) | PTFIX rot (via FBS 2-5 rot zu Klemme 10) |
| 10 | 27 | ___________ | Status zu — Rückleiter (**+24V**) | PTFIX rot (via FBS 2-5 rot zu Klemme 9) |
| 11–13 | – | (Reserve) | – | – |

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

- [ ] Kabel bestellt
- [ ] Kabel geliefert
- [ ] Farben fotografiert + dokumentiert
- [ ] Tabelle oben ausgefüllt
- [ ] CLAUDE.md aktualisiert
- [ ] Verteiler-Innenseite mit Aderfarben-Karte beklebt

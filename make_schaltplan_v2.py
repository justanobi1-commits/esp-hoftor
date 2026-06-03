# -*- coding: utf-8 -*-
# Hoftor-Schaltplan v2 - laienfreundlich
# Detailansicht: Reihenklemmen <-> Koppelrelais
# Datum: 25-05-2026

from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black, white, grey

PAGE = landscape(A3)  # 1191 x 842 pt
W, H = PAGE

OUT = r"S:/Projekte/hw-hoftor/Schaltplan_Hoftor_v2_KlemmenRelais.pdf"

c = canvas.Canvas(OUT, pagesize=PAGE)

# Farben
COL_24V    = HexColor("#D32F2F")   # rot - +24V
COL_GND    = HexColor("#1565C0")   # blau - GND
COL_CMD    = HexColor("#2E7D32")   # gruen - Befehlsleitung zum Tor
COL_STATUS = HexColor("#6A1B9A")   # violett - Statusleitung vom Tor
COL_ESP    = HexColor("#212121")   # schwarz - zum ESP
COL_LED    = HexColor("#F57C00")   # orange - LED-Pfad

BG_CARD   = HexColor("#FAFAFA")
BG_TWIN   = HexColor("#FFF3E0")
BG_KLEMME = HexColor("#ECEFF1")
BG_RIF    = HexColor("#F1F8E9")
BG_LEGEND = HexColor("#FFFDE7")
BORDER    = HexColor("#37474F")
LABEL     = HexColor("#263238")

# Helpers
def box(x, y, w, h, fill=BG_CARD, stroke=BORDER, sw=1, radius=None):
    c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(sw)
    if radius:
        c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    else:
        c.rect(x, y, w, h, fill=1, stroke=1)

def text(s, x, y, size=9, color=LABEL, anchor="c", bold=False):
    font = "Helvetica-Bold" if bold else "Helvetica"
    c.setFont(font, size); c.setFillColor(color)
    if anchor == "c": c.drawCentredString(x, y, s)
    elif anchor == "l": c.drawString(x, y, s)
    elif anchor == "r": c.drawRightString(x, y, s)

def line(x1, y1, x2, y2, color, width=1.4):
    c.setStrokeColor(color); c.setLineWidth(width); c.setDash()
    c.line(x1, y1, x2, y2)

def polyline(points, color, width=1.4):
    c.setStrokeColor(color); c.setLineWidth(width); c.setDash()
    p = c.beginPath()
    p.moveTo(points[0][0], points[0][1])
    for px, py in points[1:]:
        p.lineTo(px, py)
    c.drawPath(p, stroke=1, fill=0)

def dot(x, y, r=2.5, color=None):
    c.setFillColor(color if color else BORDER)
    c.setStrokeColor(color if color else BORDER)
    c.circle(x, y, r, fill=1, stroke=0)

# ===========================================================
# Titel
# ===========================================================
c.setFillColor(LABEL); c.setFont("Helvetica-Bold", 18)
c.drawString(40, H-40, "Hoftor – Verdrahtung Reihenklemmen → Koppelrelais")
c.setFont("Helvetica", 10)
c.drawString(40, H-58, "Detailansicht für den Verteiler-Aufbau | Stand 25-05-2026")

# ===========================================================
# REIHENKLEMMEN-LEISTE (oben)
# ===========================================================
# 10 Klemmen, davon 2 PT 2,5-TWIN an Positionen 1 und 4
# Plus FBS-Brücker zwischen Klemme 9 und 10
# Plus D-ST Endplatte rechts

KL_Y = H - 220
KL_H = 130
KL_W = 70  # breite pro klemme
KL_X0 = 60

klemmen_info = [
    ("1",  "60", "COM Haupt.",    True,  "TWIN"),
    ("2",  "61", "Open / Dauer",  False, "PT"),
    ("3",  "62", "Close",         False, "PT"),
    ("4",  "63", "COM EBD",       True,  "TWIN"),
    ("5",  "64", "Start E",       False, "PT"),
    ("6",  "65", "Open (Impuls)", False, "PT"),
    ("7",  "24", "Status offen",  False, "PT"),
    ("8",  "26", "Status zu",     False, "PT"),
    ("9",  "25", "Status off. GND", False, "PT"),
    ("10", "27", "Status zu GND", False, "PT"),
]

text("Reihenklemmen-Block (Phoenix PT 2,5)", KL_X0 + 5*KL_W, KL_Y + KL_H + 20,
     size=13, bold=True, anchor="c")
text("vom Tor (Ölflex 12G0,5)", KL_X0 + 5*KL_W, KL_Y + KL_H + 6,
     size=9, color=grey, anchor="c")

kl_pos = {}  # speichert positionen der klemmen-anschlüsse
for i, (knr, bft, fn, is_twin, ktype) in enumerate(klemmen_info):
    kx = KL_X0 + i * KL_W
    fill = BG_TWIN if is_twin else BG_KLEMME
    box(kx, KL_Y, KL_W - 2, KL_H, fill=fill, stroke=BORDER, sw=1.2)

    # TWIN-Label
    if is_twin:
        text("TWIN", kx + KL_W/2 - 1, KL_Y + KL_H - 14, size=8, bold=True, color=HexColor("#E65100"))
    else:
        text("PT 2,5", kx + KL_W/2 - 1, KL_Y + KL_H - 14, size=7, color=grey)

    # Klemmen-Nr
    text(f"#{knr}", kx + KL_W/2 - 1, KL_Y + KL_H - 32, size=14, bold=True)

    # BFT-Klemme
    text(f"BFT {bft}", kx + KL_W/2 - 1, KL_Y + KL_H - 50, size=9, color=HexColor("#1565C0"), bold=True)

    # Funktion (kann lang sein, ggf umbrechen)
    text(fn, kx + KL_W/2 - 1, KL_Y + KL_H - 65, size=7, color=grey)

    # Anschluss-Punkte
    # Oben: vom Tor (1 Punkt zentral)
    top_y = KL_Y + KL_H
    top_x = kx + KL_W/2 - 1
    dot(top_x, top_y, 2.5, COL_CMD if knr in ["1","2","3","4","5","6"] else COL_STATUS)

    # Pfeil-Linie nach oben zum Tor
    line(top_x, top_y, top_x, top_y + 14,
         COL_CMD if knr in ["1","2","3","4","5","6"] else COL_STATUS, 1.4)

    # Unten: zum Relais (1 oder 2 Punkte)
    bot_y = KL_Y
    if is_twin:
        # 2 Anschlüsse unten
        bot_x_l = kx + KL_W*0.30
        bot_x_r = kx + KL_W*0.70 - 2
        dot(bot_x_l, bot_y, 2.5, COL_CMD)
        dot(bot_x_r, bot_y, 2.5, COL_CMD)
        kl_pos[knr] = {"top": (top_x, top_y), "bot": [(bot_x_l, bot_y), (bot_x_r, bot_y)]}
    else:
        bot_x = kx + KL_W/2 - 1
        col = COL_GND if knr in ["9","10"] else (COL_CMD if knr in ["2","3","5","6"] else COL_STATUS)
        dot(bot_x, bot_y, 2.5, col)
        kl_pos[knr] = {"top": (top_x, top_y), "bot": [(bot_x, bot_y)]}

# Beschriftung "vom Tor" oberhalb
text("← vom Tor (J-Y(St)Y / Ölflex 12G0,5) →",
     KL_X0 + 5*KL_W, KL_Y + KL_H + 32, size=8, color=grey, anchor="c")

# FBS Brücker zwischen Klemme 9 und 10
br_x_l = KL_X0 + 8*KL_W + KL_W*0.7 - 2  # bot rechts von Klemme 9
br_x_r = KL_X0 + 9*KL_W + KL_W*0.3      # bot links von Klemme 10
# Da bei normalen PT 2,5 nur 1 Bot-Pin: nutze die jeweiligen positionen
br_x_l = KL_X0 + 8*KL_W + KL_W/2 - 1
br_x_r = KL_X0 + 9*KL_W + KL_W/2 - 1
br_y = KL_Y + 18
box(br_x_l - 4, br_y - 4, (br_x_r - br_x_l) + 8, 16, fill=COL_GND, stroke=COL_GND, sw=0.5)
text("FBS 2-5", (br_x_l + br_x_r)/2, br_y + 0, size=7, color=white, bold=True)
text("GND-Brücke", (br_x_l + br_x_r)/2, br_y - 10, size=6, color=COL_GND, anchor="c")

# Endplatte rechts
ep_x = KL_X0 + 10*KL_W - 2
box(ep_x, KL_Y, 12, KL_H, fill=HexColor("#FFE0B2"), stroke=BORDER, sw=1)
text("D", ep_x + 6, KL_Y + KL_H/2 - 4, size=10, bold=True, color=HexColor("#E65100"))

# CLIPFIX Endhalter links
cf_x = KL_X0 - 14
box(cf_x, KL_Y, 12, KL_H, fill=HexColor("#CFD8DC"), stroke=BORDER, sw=0.8)
text("CF", cf_x + 6, KL_Y + KL_H/2 - 4, size=8, bold=True, color=grey)

# ===========================================================
# PTFIX-Verteiler (kleine Boxen rechts neben Klemmenleiste, oben)
# ===========================================================
pt_x = KL_X0 + 10*KL_W + 30
pt_y = KL_Y + 40
pt_w = 60
pt_h = 50
# +24V
box(pt_x, pt_y + 60, pt_w, pt_h, fill=HexColor("#FFEBEE"), stroke=COL_24V, sw=1.5)
text("PTFIX", pt_x + pt_w/2, pt_y + 60 + pt_h - 14, size=8, bold=True)
text("+24 V", pt_x + pt_w/2, pt_y + 60 + pt_h - 26, size=11, bold=True, color=COL_24V)
text("rot", pt_x + pt_w/2, pt_y + 60 + 6, size=7, color=grey)

# GND
box(pt_x, pt_y, pt_w, pt_h, fill=HexColor("#E3F2FD"), stroke=COL_GND, sw=1.5)
text("PTFIX", pt_x + pt_w/2, pt_y + pt_h - 14, size=8, bold=True)
text("GND", pt_x + pt_w/2, pt_y + pt_h - 26, size=11, bold=True, color=COL_GND)
text("blau", pt_x + pt_w/2, pt_y + 6, size=7, color=grey)

# ===========================================================
# RIF-0 RELAIS (unten)
# ===========================================================

RIF_Y = 130
RIF_H = 180
RIF_W = 105
RIF_X0 = 60
RIF_GAP = 18

# Reihenfolge der Relais entsprechend der Funktions-Gruppierung
relais_info = [
    # (name, funktion1, funktion2, schaltet KontaktKlemme1, KontaktKlemme2, Spule A2 ziel, ESP-Pin)
    ("F1", "Befehl",   "öffnen",      "6",   "4",  "ESP R1", COL_ESP),
    ("F2", "Befehl",   "schließen",   "3",   "1",  "ESP R2", COL_ESP),
    ("F5", "Befehl",   "Schritt",     "5",   "4",  "ESP R3", COL_ESP),
    ("F6", "Befehl",   "Dauerauf",    "2",   "1",  "ESP R4", COL_ESP),
    ("F7", "LED",      "blau",        "PTFIX+24V", "LED+", "ESP R5", COL_LED),
    ("F8", "LED",      "rot",         "PTFIX+24V", "LED+", "ESP R6", COL_LED),
    ("F3", "Status",   "Tor offen",   "Klemme 7", "ESP DI1", "—", COL_STATUS),
    ("F4", "Status",   "Tor zu",      "Klemme 9", "ESP DI2", "—", COL_STATUS),
]

rif_pos = {}
for i, info in enumerate(relais_info):
    name, fn1, fn2, k1, k2, espdest, col = info
    rx = RIF_X0 + i * (RIF_W + RIF_GAP)
    box(rx, RIF_Y, RIF_W, RIF_H, fill=BG_RIF, stroke=col, sw=1.5, radius=4)
    # Header
    text(name, rx + RIF_W/2, RIF_Y + RIF_H - 20, size=18, bold=True, color=col)
    text(fn1, rx + RIF_W/2, RIF_Y + RIF_H - 36, size=9, color=LABEL)
    text(fn2, rx + RIF_W/2, RIF_Y + RIF_H - 47, size=10, bold=True, color=col)

    # Phoenix RIF-0 Beschriftung
    text("Phoenix RIF-0", rx + RIF_W/2, RIF_Y + 8, size=6, color=grey)

    # Spulen-Anschluss (A1, A2) oben
    a1x = rx + RIF_W*0.25
    a2x = rx + RIF_W*0.45
    spy = RIF_Y + RIF_H
    dot(a1x, spy, 2.5, COL_24V)
    dot(a2x, spy, 2.5, col)
    text("A1", a1x, spy + 4, size=6, color=COL_24V, bold=True)
    text("A2", a2x, spy + 4, size=6, color=col, bold=True)

    # Kontakt-Anschluss (11, 14) oben (rechts)
    k11x = rx + RIF_W*0.70
    k14x = rx + RIF_W*0.90
    dot(k11x, spy, 2.5, BORDER)
    dot(k14x, spy, 2.5, BORDER)
    text("11", k11x, spy + 4, size=6, color=BORDER, bold=True)
    text("14", k14x, spy + 4, size=6, color=BORDER, bold=True)

    rif_pos[name] = {
        "A1": (a1x, spy),
        "A2": (a2x, spy),
        "K11": (k11x, spy),
        "K14": (k14x, spy)
    }

    # Verdrahtungs-Info im Relais-Block
    info_y = RIF_Y + 80
    # Block für die Anschlussziele
    text("Anschlüsse:", rx + RIF_W/2, info_y + 30, size=7, bold=True, color=grey)
    text(f"A1 = +24 V", rx + 10, info_y + 16, size=7, anchor="l", color=COL_24V)
    text(f"A2 = {espdest}", rx + 10, info_y + 6, size=7, anchor="l", color=col)
    text(f"11 → {k1}", rx + 10, info_y - 4, size=7, anchor="l")
    text(f"14 → {k2}", rx + 10, info_y - 14, size=7, anchor="l")

# ===========================================================
# VERBINDUNGEN ZEICHNEN
# ===========================================================

# Für jedes Befehls-Relais: 2 Verbindungslinien zu den Klemmen
# F1: 11 → Klemme 6, 14 → Klemme 4 (TWIN slot 2)
# F2: 11 → Klemme 3, 14 → Klemme 1 (TWIN slot 1)
# F5: 11 → Klemme 5, 14 → Klemme 4 (TWIN slot 1)
# F6: 11 → Klemme 2, 14 → Klemme 1 (TWIN slot 2)

# Mapping (Relais, Anschluss) → (Klemme, slot index)
befehl_verbindungen = [
    ("F1", "K11", "6", 0),
    ("F1", "K14", "4", 1),
    ("F2", "K11", "3", 0),
    ("F2", "K14", "1", 0),
    ("F5", "K11", "5", 0),
    ("F5", "K14", "4", 0),
    ("F6", "K11", "2", 0),
    ("F6", "K14", "1", 1),
]
for rname, ranschluss, klemme, slot_idx in befehl_verbindungen:
    rxp, ryp = rif_pos[rname][ranschluss]
    if slot_idx < len(kl_pos[klemme]["bot"]):
        kxp, kyp = kl_pos[klemme]["bot"][slot_idx]
    else:
        kxp, kyp = kl_pos[klemme]["bot"][0]
    # Polyline mit Knick
    midy = (ryp + kyp) / 2
    polyline([(rxp, ryp), (rxp, midy), (kxp, midy), (kxp, kyp)], COL_CMD, 1.2)

# F3: Spule A2 → Klemme 7
# F4: Spule A2 → Klemme 9
status_verb = [("F3", "7"), ("F4", "9")]
for rname, klemme in status_verb:
    rxp, ryp = rif_pos[rname]["A2"]
    kxp, kyp = kl_pos[klemme]["bot"][0]
    midy = (ryp + kyp) / 2
    polyline([(rxp, ryp), (rxp, midy + 20), (kxp, midy + 20), (kxp, kyp)], COL_STATUS, 1.2)

# F3-K11: zu GND (PTFIX blau) — wir zeigen das als kurze Linie nach rechts mit Label
# F3-K14: zu ESP DI1 — Pfeil weg
# F4-K11: zu GND
# F4-K14: zu ESP DI2 — Pfeil weg

# Linien Klemme 9 → GND (PTFIX blau via FBS auch)
# Klemme 9 und 10 GND sammeln und 1 Linie zum PTFIX-GND
gnd_pt_x = pt_x + pt_w/2
gnd_pt_y = pt_y
# Sammler-Linie unter klemmen 9+10 nach rechts zum PTFIX
sammler_y = KL_Y - 30
k9_x = kl_pos["9"]["bot"][0][0]
k10_x = kl_pos["10"]["bot"][0][0]
# Klemme 9 nach unten
polyline([(k9_x, KL_Y), (k9_x, sammler_y),
          (gnd_pt_x, sammler_y), (gnd_pt_x, pt_y + pt_h)], COL_GND, 1.5)
# Klemme 10 nach unten
polyline([(k10_x, KL_Y), (k10_x, sammler_y)], COL_GND, 1.5)

text("GND → PTFIX blau", (k10_x + gnd_pt_x)/2, sammler_y + 4, size=7, color=COL_GND, bold=True)

# +24V vom PTFIX rot zu allen Relais A1
v24_pt_x = pt_x + pt_w/2
v24_pt_y = pt_y + 60  # bottom of red PTFIX
# Sammelschiene unter allen RIF-0, von rechts kommend
v24_rail_y = RIF_Y + RIF_H + 40
# Linie von PTFIX rot nach unten und links
polyline([(v24_pt_x, v24_pt_y), (v24_pt_x, v24_rail_y),
          (RIF_X0 + RIF_W*0.25, v24_rail_y)], COL_24V, 2.0)
# Stichleitungen zu jedem A1
for name in ["F1","F2","F5","F6","F7","F8","F3","F4"]:
    a1x, a1y = rif_pos[name]["A1"]
    line(a1x, v24_rail_y, a1x, a1y, COL_24V, 1.2)

text("+24 V Sammelschiene zu allen Relais-Spulen", RIF_X0 + 200, v24_rail_y + 8,
     size=8, color=COL_24V, bold=True, anchor="l")

# F7, F8 K11 = +24V (PTFIX) — kurze Linie unten zum LED-Pfad
# Im Block-Text schon erwähnt, deshalb hier minimal markieren

# F3, F4: K11 (=GND), K14 (zu ESP DI)
# Hier nur Hinweis-Pfeile

# ESP-Pfeile rechts/oben für die Befehls-Relais A2
for name in ["F1","F2","F5","F6","F7","F8"]:
    a2x, a2y = rif_pos[name]["A2"]
    polyline([(a2x, a2y), (a2x, a2y + 25)], COL_ESP, 1.2)
    text("ESP", a2x, a2y + 30, size=6, color=COL_ESP, bold=True)

# F3, F4: K14 zu ESP DI
for name in ["F3","F4"]:
    k14x, k14y = rif_pos[name]["K14"]
    polyline([(k14x, k14y), (k14x, k14y + 25)], COL_ESP, 1.2)
    text("ESP DI", k14x, k14y + 30, size=6, color=COL_ESP, bold=True)

# F3, F4: K11 zu PTFIX GND (Hinweis im Text-Block bereits)
for name in ["F3","F4"]:
    k11x, k11y = rif_pos[name]["K11"]
    polyline([(k11x, k11y), (k11x, k11y + 12)], COL_GND, 1.2)
    text("GND", k11x, k11y + 17, size=6, color=COL_GND, bold=True)

# ===========================================================
# LEGENDE (unten)
# ===========================================================
leg_y = 70
leg_x = 60
leg_w = W - 120
leg_h = 50
box(leg_x, leg_y - 10, leg_w, leg_h, fill=BG_LEGEND, stroke=BORDER, sw=1)
text("Legende – Aderfarben und Symbole", leg_x + 10, leg_y + 28,
     size=10, bold=True, anchor="l")

entries = [
    (COL_24V, "Rot = +24 V Versorgung (PSU → PTFIX → Relais-Spulen A1)"),
    (COL_GND, "Blau = GND/0 V (PSU → PTFIX → GND-Sammelpunkte)"),
    (COL_CMD, "Grün = Befehlsleitung (Klemme ↔ Befehls-Relais Kontakte)"),
    (COL_STATUS, "Violett = Statusleitung (Klemme → Status-Relais Spule)"),
    (COL_ESP, "Schwarz = Anschluss zum ESP (Relaisseite oder DI-Eingang)"),
    (COL_LED, "Orange = LED-Pfad (Relais F7/F8 schaltet +24 V auf LED)"),
]
col_w = (leg_w - 20) / 3
for i, (col, label) in enumerate(entries):
    row = i // 3
    col_i = i % 3
    ex = leg_x + 10 + col_i * col_w
    ey = leg_y + 12 - row * 14
    line(ex, ey, ex + 24, ey, col, 2.8)
    text(label, ex + 30, ey - 3, size=8, anchor="l")

# Sonder-Hinweise
hint_y = 35
c.setFillColor(grey); c.setFont("Helvetica-Oblique", 7)
c.drawString(60, hint_y, "PT 2,5-TWIN (Klemme 1 + 4): 1 Eingang oben, 2 Ausgänge unten – versorgt 2 Relais-Kontakte mit der gleichen BFT-COM-Klemme.")
c.drawString(60, hint_y - 10, "FBS 2-5 Steckbrücke: verbindet die GND-Klemmen 9 und 10 intern – 1 GND-Ader zum PTFIX reicht.")
c.drawString(60, hint_y - 20, "D-ST 2,5 Endplatte rechts: deckt die offene Seite der letzten Klemme ab. CLIPFIX 35 Endhalter (CF) hält die Reihe seitlich auf der Hutschiene fest.")
c.drawRightString(W - 60, 25, "Datei: Schaltplan_Hoftor_v2_KlemmenRelais.pdf | Erstellt: 25-05-2026")

c.showPage()
c.save()
print(f"PDF erstellt: {OUT}")

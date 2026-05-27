# -*- coding: utf-8 -*-
# Hoftor-Schaltplan v1 - laienfreundlich
# Datum: 25-05-2026

from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import (
    HexColor, black, white, red, blue, grey, green, orange, yellow
)

PAGE = landscape(A3)  # 1191 x 842 pt
W, H = PAGE

OUT = r"C:/Users/obero/OneDrive/claude/.claude/esp/hoftor/Schaltplan_Hoftor_v1.pdf"

c = canvas.Canvas(OUT, pagesize=PAGE)

# Farben
COL_24V = HexColor("#D32F2F")        # rot - +24V
COL_GND = HexColor("#1565C0")        # blau - GND
COL_SIG_OUT = HexColor("#212121")    # schwarz - ESP-Relais -> Finder-Spulen
COL_SIG_IN = HexColor("#616161")     # grau - Status -> ESP
COL_EXT = HexColor("#2E7D32")        # gruen - Tor-Befehle extern
COL_230 = HexColor("#F57C00")        # orange - 230V

BG_VERT = HexColor("#ECEFF1")
BG_ROW = HexColor("#FAFAFA")
BORDER = HexColor("#37474F")
LABEL = HexColor("#263238")

# Hilfsfunktionen
def box(x, y, w, h, fill=BG_ROW, stroke=BORDER, sw=1):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(sw)
    c.rect(x, y, w, h, fill=1, stroke=1)

def text(s, x, y, size=9, color=LABEL, anchor="c", bold=False):
    font = "Helvetica-Bold" if bold else "Helvetica"
    c.setFont(font, size)
    c.setFillColor(color)
    if anchor == "c":
        c.drawCentredString(x, y, s)
    elif anchor == "l":
        c.drawString(x, y, s)
    elif anchor == "r":
        c.drawRightString(x, y, s)

def line(x1, y1, x2, y2, color, width=1.6, dash=None):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    if dash:
        c.setDash(dash, 2)
    else:
        c.setDash()
    c.line(x1, y1, x2, y2)
    c.setDash()

def polyline(points, color, width=1.6):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.setDash()
    p = c.beginPath()
    p.moveTo(points[0][0], points[0][1])
    for px, py in points[1:]:
        p.lineTo(px, py)
    c.drawPath(p, stroke=1, fill=0)

def dot(x, y, r=2.5, color=None):
    c.setFillColor(color if color else BORDER)
    c.setStrokeColor(color if color else BORDER)
    c.circle(x, y, r, fill=1, stroke=0)

# ============================================================
# Titel
# ============================================================
c.setFillColor(LABEL)
c.setFont("Helvetica-Bold", 20)
c.drawString(40, H - 40, "Hoftor-Steuerung – Schaltplan")
c.setFont("Helvetica", 11)
c.drawString(40, H - 58, "ESP32 ersetzt 3 Shelly Uni Plus | Verteiler 3 × 12 TE | Stand 25-05-2026")

# ============================================================
# Verteilerkasten (Hintergrund)
# ============================================================
VX, VY, VW, VH = 60, 130, 820, 600
box(VX, VY, VW, VH, fill=BG_VERT, stroke=BORDER, sw=2)
text("VERTEILER 3 × 12 TE", VX + VW/2, VY + VH - 18, size=11, bold=True)

# 3 Reihen Layout
row_h = 150
row_y = [VY + 30, VY + 30 + row_h + 20, VY + 30 + (row_h + 20)*2]
# row_y[0] = unterste, row_y[2] = oberste

for i, ry in enumerate(row_y):
    box(VX + 20, ry, VW - 40, row_h, fill=BG_ROW, stroke=BORDER, sw=0.5)
    text(f"Reihe {3-i}", VX + 28, ry + row_h - 12, size=8, anchor="l", color=grey)

# ============================================================
# REIHE 1 (oben) - Versorgung
# ============================================================
r1y = row_y[2]
r1cy = r1y + row_h/2

# Geraete in Reihe 1
gx = VX + 60
gw = 90
gh = 80
gap = 20

# ABB Ausschalter
abb_x = gx
box(abb_x, r1cy - gh/2, gw, gh, fill=HexColor("#FFF3E0"))
text("ABB", abb_x + gw/2, r1cy + 15, size=11, bold=True)
text("Ausschalter", abb_x + gw/2, r1cy + 2, size=8)
text("230V Hand-Aus", abb_x + gw/2, r1cy - 12, size=7, color=grey)

# PSU
psu_x = abb_x + gw + gap
box(psu_x, r1cy - gh/2, gw + 20, gh, fill=HexColor("#E8F5E9"))
text("DEWIN PSU", psu_x + (gw+20)/2, r1cy + 18, size=11, bold=True)
text("24 V / 1,5 A", psu_x + (gw+20)/2, r1cy + 4, size=9)
text("230V → 24V DC", psu_x + (gw+20)/2, r1cy - 12, size=7, color=grey)

# Sicherung
sic_x = psu_x + gw + 20 + gap
box(sic_x, r1cy - gh/2, gw - 20, gh, fill=HexColor("#FFFDE7"))
text("Sicherung", sic_x + (gw-20)/2, r1cy + 12, size=10, bold=True)
text("2 A T", sic_x + (gw-20)/2, r1cy, size=10)
text("Glas 5×20", sic_x + (gw-20)/2, r1cy - 12, size=7, color=grey)

# PTFIX rot +24V
pr_x = sic_x + (gw-20) + gap
box(pr_x, r1cy - gh/2, gw, gh, fill=HexColor("#FFEBEE"), stroke=COL_24V, sw=1.5)
text("Verteiler", pr_x + gw/2, r1cy + 18, size=10, bold=True)
text("+24 V", pr_x + gw/2, r1cy + 4, size=12, bold=True, color=COL_24V)
text("WAGO 2009-305", pr_x + gw/2, r1cy - 14, size=7, color=grey)

# PTFIX blau GND
pb_x = pr_x + gw + gap
box(pb_x, r1cy - gh/2, gw, gh, fill=HexColor("#E3F2FD"), stroke=COL_GND, sw=1.5)
text("Verteiler", pb_x + gw/2, r1cy + 18, size=10, bold=True)
text("GND (0 V)", pb_x + gw/2, r1cy + 4, size=12, bold=True, color=COL_GND)
text("WAGO 2009-305", pb_x + gw/2, r1cy - 14, size=7, color=grey)

# Verbindungen Reihe 1
# 230V von links oben in ABB
line(40, H - 100, 40, r1cy, COL_230, 2.2)
line(40, r1cy, abb_x, r1cy, COL_230, 2.2)
text("230 V von B16", 50, H - 90, size=9, anchor="l", color=COL_230, bold=True)

# ABB -> PSU
line(abb_x + gw, r1cy, psu_x, r1cy, COL_230, 2.2)

# PSU -> Sicherung (+24V)
line(psu_x + gw + 20, r1cy + 15, sic_x, r1cy + 15, COL_24V, 2.0)
# Sicherung -> Verteiler rot
line(sic_x + gw - 20, r1cy + 15, pr_x, r1cy + 15, COL_24V, 2.0)
# PSU -> Verteiler blau (GND geht aussen rum unten)
polyline([(psu_x + gw + 20, r1cy - 15),
          (psu_x + gw + 20 + 8, r1cy - 15),
          (psu_x + gw + 20 + 8, r1cy - gh/2 - 15),
          (pb_x + gw/2, r1cy - gh/2 - 15),
          (pb_x + gw/2, r1cy - gh/2)], COL_GND, 2.0)

# Beschriftungen Adern
text("+24 V", (sic_x + pr_x)/2, r1cy + 22, size=8, color=COL_24V, bold=True)
text("GND", psu_x + gw + 30, r1cy - gh/2 - 22, size=8, color=COL_GND, bold=True)

# ============================================================
# REIHE 2 (Mitte) - Finder-Relais + externe Klemmen
# ============================================================
r2y = row_y[1]
r2cy = r2y + row_h/2

# 8 Finder-Relais
fw = 50
fh = 100
fgap = 4
f_start_x = VX + 50
finder_info = [
    ("F1", "Befehl", "öffnen", COL_SIG_OUT),
    ("F2", "Befehl", "schließen", COL_SIG_OUT),
    ("F5", "Schritt", "auf/zu", COL_SIG_OUT),
    ("F6", "Dauerauf", "halten", COL_SIG_OUT),
    ("F7", "LED", "blau", COL_SIG_OUT),
    ("F8", "LED", "rot", COL_SIG_OUT),
    ("F3", "Status", "Tor offen", COL_SIG_IN),
    ("F4", "Status", "Tor zu", COL_SIG_IN),
]
finder_pos = {}
for i, (name, line1, line2, col) in enumerate(finder_info):
    fx = f_start_x + i * (fw + fgap)
    # gesonderter Abstand zwischen ESP-gesteuerten (F1..F8) und Tor-gesteuerten (F3,F4)
    if i == 6:
        fx += 15
    box(fx, r2cy - fh/2, fw, fh, fill=HexColor("#FAFAFA"), stroke=col, sw=1.5)
    text(name, fx + fw/2, r2cy + fh/2 - 16, size=12, bold=True, color=col)
    text(line1, fx + fw/2, r2cy + fh/2 - 30, size=8)
    text(line2, fx + fw/2, r2cy + fh/2 - 40, size=8)
    text("Finder", fx + fw/2, r2cy - fh/2 + 18, size=7, color=grey)
    text("Relais", fx + fw/2, r2cy - fh/2 + 8, size=7, color=grey)
    # Spulen-Anschluss oben
    dot(fx + fw*0.35, r2cy + fh/2, 2)
    dot(fx + fw*0.65, r2cy + fh/2, 2)
    text("A1", fx + fw*0.35, r2cy + fh/2 + 4, size=6, color=grey)
    text("A2", fx + fw*0.65, r2cy + fh/2 + 4, size=6, color=grey)
    # Kontakt-Anschluss unten
    dot(fx + fw*0.35, r2cy - fh/2, 2)
    dot(fx + fw*0.65, r2cy - fh/2, 2)
    finder_pos[name] = (fx, fx + fw, fx + fw*0.35, fx + fw*0.65, r2cy + fh/2, r2cy - fh/2)

# Steckbruecke ueber F1..F8 (A1-Seite) +24V
last_esp_finder_x = finder_pos["F8"][1]
first_esp_finder_x = finder_pos["F1"][2]
bridge_y = r2cy + fh/2 + 14
line(first_esp_finder_x, bridge_y, last_esp_finder_x - (fw - fw*0.35), bridge_y, COL_24V, 2.2)
# Stecker
for fname in ["F1","F2","F5","F6","F7","F8"]:
    fx_dot = finder_pos[fname][2]
    line(fx_dot, finder_pos[fname][4], fx_dot, bridge_y, COL_24V, 1.5)
    dot(fx_dot, bridge_y, 2.5, COL_24V)
text("Steckbrücke +24 V", (first_esp_finder_x + last_esp_finder_x - fw + fw*0.35)/2,
     bridge_y + 6, size=8, color=COL_24V, bold=True)

# Externer Klemmenblock (rechts)
kbx = finder_pos["F4"][1] + 30
kbw = 180
kbh = fh
box(kbx, r2cy - kbh/2, kbw, kbh, fill=HexColor("#F1F8E9"), stroke=COL_EXT, sw=1.5)
text("10 × WAGO 2001-1671", kbx + kbw/2, r2cy + kbh/2 - 14, size=9, bold=True)
text("Trennklemmen", kbx + kbw/2, r2cy + kbh/2 - 26, size=8)
# Klemmen darstellen
for k in range(10):
    cx = kbx + 12 + k * 16
    box(cx - 6, r2cy - 25, 12, 50, fill=white, stroke=COL_EXT, sw=0.6)
    text(str(k+1), cx, r2cy - 30, size=7)
    dot(cx, r2cy - kbh/2, 1.8, COL_EXT)
text("Externe Klemmen zum Tor", kbx + kbw/2, r2cy - kbh/2 + 8, size=7, color=grey)

# ============================================================
# REIHE 3 (unten) - ESP
# ============================================================
r3y = row_y[0]
r3cy = r3y + row_h/2

esp_x = VX + 60
esp_w = 460
esp_h = 110
box(esp_x, r3cy - esp_h/2, esp_w, esp_h, fill=HexColor("#FFF8E1"), stroke=BORDER, sw=2)
text("Waveshare ESP32-S3-POE-ETH-8DI-8RO", esp_x + esp_w/2, r3cy + esp_h/2 - 14, size=12, bold=True)
text("ESP-Steuerung (ersetzt 3 Shelly Uni Plus)", esp_x + esp_w/2, r3cy + esp_h/2 - 28, size=8, color=grey)

# RJ45 / PoE
rj_w = 50
rj_h = 32
rj_x = esp_x - rj_w - 10
box(rj_x, r3cy - rj_h/2, rj_w, rj_h, fill=HexColor("#E0F2F1"))
text("RJ45", rj_x + rj_w/2, r3cy + 4, size=9, bold=True)
text("PoE", rj_x + rj_w/2, r3cy - 8, size=8, color=COL_EXT)

# Verbindung RJ45 -> ESP
line(rj_x + rj_w, r3cy, esp_x, r3cy, COL_EXT, 2.0)
# PoE-Kabel nach links aus dem Verteiler
line(rj_x, r3cy, VX - 5, r3cy, COL_EXT, 2.0)
text("PoE-Switch", VX - 8, r3cy + 8, size=8, anchor="r", color=COL_EXT, bold=True)
text("(LAN + Strom)", VX - 8, r3cy - 4, size=7, anchor="r", color=COL_EXT)

# Relais R1..R8 unten an ESP
rel_y = r3cy - esp_h/2
rel_positions = {}
for i in range(8):
    rx = esp_x + 30 + i * 28
    dot(rx, rel_y, 2.5, COL_SIG_OUT)
    text(f"R{i+1}", rx, rel_y - 10, size=8, bold=True)
    rel_positions[f"R{i+1}"] = rx

# DI1..DI8 oben rechts an ESP (eigentlich unten, aber wir nutzen die rechte Haelfte)
di_y = r3cy - esp_h/2
di_positions = {}
for i in range(8):
    dx = esp_x + 260 + i * 22
    dot(dx, di_y, 2.5, COL_SIG_IN)
    text(f"DI{i+1}", dx, di_y - 10, size=7, bold=True, color=COL_SIG_IN)
    di_positions[f"DI{i+1}"] = dx

# Hinweis-Block neben ESP
hb_x = esp_x + esp_w + 20
hb_w = 280
hb_h = esp_h
box(hb_x, r3cy - hb_h/2, hb_w, hb_h, fill=HexColor("#FAFAFA"))
text("ESP-Belegung", hb_x + hb_w/2, r3cy + hb_h/2 - 14, size=10, bold=True)
zuord = [
    ("R1 → F1", "Befehl Tor öffnen"),
    ("R2 → F2", "Befehl Tor schließen"),
    ("R3 → F5", "Befehl Schritt (öffnen/stopp/schließen)"),
    ("R4 → F6", "Befehl Dauerauf"),
    ("R5 → F7", "LED blau (Tor offen)"),
    ("R6 → F8", "LED rot (Dauerauf aktiv)"),
    ("DI1 ← F3", "Status: Tor offen"),
    ("DI2 ← F4", "Status: Tor geschlossen"),
    ("DI3 ← Taster", "Taster Dauerauf-Auslöser"),
]
for i, (l, r) in enumerate(zuord):
    y = r3cy + hb_h/2 - 28 - i * 9
    text(l, hb_x + 10, y, size=7, anchor="l", bold=True)
    text(r, hb_x + 90, y, size=7, anchor="l", color=grey)

# ============================================================
# VERBINDUNGEN ZWISCHEN DEN REIHEN
# ============================================================

# +24V vom Verteiler rot zur Steckbrücke der Finder (Reihe 1 -> Reihe 2 oben)
src_x = pr_x + 20
src_y = r1cy - gh/2
brg_x = (first_esp_finder_x + last_esp_finder_x - fw + fw*0.35)/2
polyline([(src_x, src_y), (src_x, src_y - 20),
          (brg_x, src_y - 20), (brg_x, bridge_y + 12)], COL_24V, 2.0)

# +24V auch zum ESP (VIN nicht noetig wegen PoE - aber Hinweis)
# wir lassen das hier weg um den Plan ruhig zu halten

# GND vom Verteiler blau zu ESP DI-COM
gnd_src_x = pb_x + gw/2
gnd_src_y = r1cy - gh/2
gnd_target_x = esp_x + esp_w - 20
gnd_target_y = r3cy + esp_h/2
polyline([(gnd_src_x, gnd_src_y),
          (gnd_src_x, gnd_src_y - 20),
          (gnd_target_x, gnd_src_y - 20),
          (gnd_target_x, gnd_target_y)], COL_GND, 2.0)
text("GND zum ESP", gnd_target_x + 5, gnd_src_y - 16, size=7, anchor="l", color=COL_GND)

# GND zu F3/F4 Spulen (von Tor versorgt - wir zeigen Rueckleiter)
for fn in ["F3", "F4"]:
    fx_a1 = finder_pos[fn][2]
    polyline([(fx_a1, finder_pos[fn][4]),
              (fx_a1, finder_pos[fn][4] + 8),
              (fx_a1 + 25, finder_pos[fn][4] + 8)], COL_GND, 1.4)

# ESP-Relais R1..R6 -> Finder F1,F2,F5,F6,F7,F8 (A2-Seite)
rel_to_finder = [
    ("R1", "F1"), ("R2", "F2"), ("R3", "F5"),
    ("R4", "F6"), ("R5", "F7"), ("R6", "F8")
]
for rname, fname in rel_to_finder:
    rx = rel_positions[rname]
    ry = rel_y
    fx_a2 = finder_pos[fname][3]
    fy = finder_pos[fname][4]
    polyline([(rx, ry), (rx, ry + 18), (fx_a2, ry + 18), (fx_a2, fy)], COL_SIG_OUT, 1.4)

# Finder F3, F4 Kontakte -> ESP DI1, DI2 (Status)
status_map = [("F3", "DI1"), ("F4", "DI2")]
for fname, dname in status_map:
    fc_x = finder_pos[fname][3]  # Kontakt unten Mitte
    fc_y = finder_pos[fname][5]
    dx = di_positions[dname]
    dy = di_y
    polyline([(fc_x, fc_y), (fc_x, fc_y - 20),
              (dx, fc_y - 20), (dx, dy)], COL_SIG_IN, 1.4)

# Finder F1, F2, F5, F6 Kontakte -> Externe Klemmen (Tor-Befehle)
finder_to_klemme = [("F1", 0), ("F2", 2), ("F5", 4), ("F6", 6)]
for fname, kidx in finder_to_klemme:
    fc_x = finder_pos[fname][3]
    fc_y = finder_pos[fname][5]
    kx = kbx + 12 + kidx * 16
    polyline([(fc_x, fc_y), (fc_x, fc_y - 12),
              (kx, fc_y - 12), (kx, r2cy - 25)], COL_EXT, 1.4)

# F3, F4 Spulen werden von externen Klemmen (Tor) getrieben - das ist die Statusseite
# F3 Spule A2 <- externe Klemme
for fn, kidx in [("F3", 8), ("F4", 9)]:
    fx_a2 = finder_pos[fn][3]
    fy = finder_pos[fn][4]
    kx = kbx + 12 + kidx * 16
    polyline([(kx, r2cy - 25), (kx, fy + 25),
              (fx_a2, fy + 25), (fx_a2, fy)], COL_EXT, 1.4)

# ============================================================
# EXTERNE GERAETE (rechts vom Verteiler)
# ============================================================
ext_x = VX + VW + 30
# Hoftor
tor_x = ext_x
tor_y = r2cy
tor_w = 200
tor_h = 200
# (wir bleiben innerhalb der A3 - rechts ist noch Platz wenn wir den Verteiler verschmaelern)
# Stattdessen: Hoftor unter dem Klemmenblock anzeigen
tor_x = kbx + 10
tor_y = VY - 75
tor_w = kbw - 20
tor_h = 60
box(tor_x, tor_y, tor_w, tor_h, fill=HexColor("#EFEBE9"), stroke=BORDER, sw=2)
text("HOFTOR (BFT)", tor_x + tor_w/2, tor_y + tor_h - 15, size=11, bold=True)
text("Toranlage außen", tor_x + tor_w/2, tor_y + tor_h - 28, size=8, color=grey)
text("Anschluss via J-Y(St)Y 4×2×0,8", tor_x + tor_w/2, tor_y + 10, size=7, color=grey)

# Kabel von Klemmenblock zum Tor
for k in range(10):
    cx = kbx + 12 + k * 16
    polyline([(cx, r2cy - kbh/2),
              (cx, tor_y + tor_h)], COL_EXT, 1.0)

# LEDs unten links unter dem Tor-Block
led_x = tor_x - 110
led_y = tor_y + 10
# LED blau
box(led_x, led_y, 50, 40, fill=HexColor("#E3F2FD"), stroke=COL_GND, sw=1.5)
text("LED", led_x + 25, led_y + 28, size=9, bold=True, color=COL_GND)
text("blau", led_x + 25, led_y + 14, size=8, color=COL_GND)
text("Tor offen", led_x + 25, led_y + 2, size=6, color=grey)
# LED rot
box(led_x - 60, led_y, 50, 40, fill=HexColor("#FFEBEE"), stroke=COL_24V, sw=1.5)
text("LED", led_x - 35, led_y + 28, size=9, bold=True, color=COL_24V)
text("rot", led_x - 35, led_y + 14, size=8, color=COL_24V)
text("Dauerauf", led_x - 35, led_y + 2, size=6, color=grey)

# F7 Kontakt -> LED blau
f7_cx = finder_pos["F7"][3]
f7_cy = finder_pos["F7"][5]
polyline([(f7_cx, f7_cy),
          (f7_cx, f7_cy - 12),
          (led_x + 25, f7_cy - 12),
          (led_x + 25, led_y + 40)], COL_SIG_OUT, 1.4)

# F8 Kontakt -> LED rot
f8_cx = finder_pos["F8"][3]
f8_cy = finder_pos["F8"][5]
polyline([(f8_cx, f8_cy),
          (f8_cx, f8_cy - 8),
          (led_x - 35, f8_cy - 8),
          (led_x - 35, led_y + 40)], COL_SIG_OUT, 1.4)

# ============================================================
# LEGENDE (unten)
# ============================================================
leg_y = 60
leg_x = 60
box(leg_x, leg_y - 10, W - 120, 50, fill=white, stroke=BORDER, sw=1)
text("Legende – Aderfarben", leg_x + 10, leg_y + 28, size=10, bold=True, anchor="l")

entries = [
    (COL_230, "Orange = 230 V Wechselspannung (Netzseite)"),
    (COL_24V, "Rot = +24 V DC (Versorgung)"),
    (COL_GND, "Blau = GND / 0 V (Masse)"),
    (COL_SIG_OUT, "Schwarz = Steuersignal ESP → Finder-Spule"),
    (COL_SIG_IN, "Grau = Statussignal Finder-Kontakt → ESP"),
    (COL_EXT, "Grün = externe Verbindung zum Hoftor / PoE-Netz"),
]
col_w = (W - 140) / 3
for i, (col, label) in enumerate(entries):
    row = i // 3
    col_i = i % 3
    ex = leg_x + 10 + col_i * col_w
    ey = leg_y + 12 - row * 14
    line(ex, ey, ex + 24, ey, col, 2.5)
    text(label, ex + 30, ey - 3, size=8, anchor="l")

# Fussnote
c.setFont("Helvetica-Oblique", 7)
c.setFillColor(grey)
c.drawString(60, 30, "Hinweis: Vereinfachte Übersicht für Laien – exakte Klemmenbelegung folgt in separater Tabelle.")
c.drawRightString(W - 60, 30, "Datei: Schaltplan_Hoftor_v1.pdf | Erstellt: 25-05-2026")

c.showPage()
c.save()
print(f"PDF erstellt: {OUT}")

"""Texturi PBR procedurale: culoare (sRGB) + harta MR (R = clearcoat, G = rugozitate, B = metalic).

Toate desenele sunt in metri, in coordonatele suprafetei:
  - laterale: (x, y), proiectie pe planul flancului;
  - fata / spate: (a, y), a = lungimea de arc desfasurata de la axa masinii, privita din fata / spate.
"""

from __future__ import annotations

import io
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import geometrie as g

FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"
FONT = "C:/Windows/Fonts/arial.ttf"

# Star Silver III metalizat (cod Opel Z157 / 2AU), culoarea din poza de referinta.
PAINT = (168, 172, 176)
PAINT_MR = (255, 92, 190)       # clearcoat 1, rugozitate 0.36, metalic 0.75
GLASS = (30, 35, 41)
GLASS_MR = (255, 10, 0)
BLACK = (9, 9, 10)            # ornamente negre lucioase (rame geamuri, stalpi)
BLACK_MR = (200, 70, 0)
PLASTIC = (30, 31, 33)          # plastic negru texturat (grile, bare inferioare)
PLASTIC_MR = (0, 175, 0)
GAP = (20, 20, 21)              # rosturi intre panouri
GAP_MR = (0, 210, 0)
CHROME = (236, 238, 241)
CHROME_MR = (255, 22, 255)
RED = (150, 10, 16)
RED_MR = (255, 28, 0)
CLEAR = (205, 208, 212)
CLEAR_MR = (255, 18, 60)


# Centrele numerelor (a, y) si marimea placutei UE; cardul le rescrie la rulare.
FRONT_PLATE = (0.0, 0.518)
REAR_PLATE = (0.0, 0.693)
PLATE_SIZE = (0.52, 0.11)


def srgb_to_linear(c):
    c = c / 255.0
    return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92


def linear_color(rgb):
    return tuple(srgb_to_linear(c) for c in rgb) + (1.0,)


class Painter:
    def __init__(self, w, h, xr, yr, base=None, base_mr=None, ss=3, emissive=False):
        base = base or PAINT
        base_mr = base_mr or PAINT_MR
        self.w, self.h, self.ss = w, h, ss
        self.x0, self.x1 = xr
        self.y0, self.y1 = yr
        self.col = Image.new("RGB", (w * ss, h * ss), base)
        self.mr = Image.new("RGB", (w * ss, h * ss), base_mr)
        self.dc = ImageDraw.Draw(self.col)
        self.dm = ImageDraw.Draw(self.mr)
        # masca lampilor: R = faruri / stopuri, G = semnalizari
        self.em = Image.new("RGB", (w * ss, h * ss), (0, 0, 0)) if emissive else None
        self.de = ImageDraw.Draw(self.em) if emissive else None

    # coordonate
    def p(self, x, y):
        return ((x - self.x0) / (self.x1 - self.x0) * self.w * self.ss,
                (self.y1 - y) / (self.y1 - self.y0) * self.h * self.ss)

    def kx(self):
        return self.w * self.ss / (self.x1 - self.x0)

    def ky(self):
        return self.h * self.ss / (self.y1 - self.y0)

    # primitive
    def poly(self, pts, col, mr=None, em=None):
        q = [self.p(x, y) for x, y in pts]
        self.dc.polygon(q, fill=col)
        if mr:
            self.dm.polygon(q, fill=mr)
        if em is not None and self.de:
            self.de.polygon(q, fill=em)

    def ellipse(self, cx, cy, rx, ry, col, mr=None, em=None):
        a, b = self.p(cx - rx, cy + ry), self.p(cx + rx, cy - ry)
        self.dc.ellipse([a, b], fill=col)
        if mr:
            self.dm.ellipse([a, b], fill=mr)
        if em is not None and self.de:
            self.de.ellipse([a, b], fill=em)

    def circle(self, cx, cy, r, col, mr=None, em=None):
        self.ellipse(cx, cy, r, r, col, mr, em)

    def ring(self, cx, cy, r_out, r_in, col, mr, inner_col, inner_mr):
        self.circle(cx, cy, r_out, col, mr)
        self.circle(cx, cy, r_in, inner_col, inner_mr)

    def line(self, pts, width, col, mr=None):
        q = [self.p(x, y) for x, y in pts]
        px = max(1, int(round(width * 0.5 * (self.kx() + self.ky()))))
        self.dc.line(q, fill=col, width=px, joint="curve")
        if mr:
            self.dm.line(q, fill=mr, width=px, joint="curve")

    def rrect(self, x0, y0, x1, y1, r, col, mr=None, em=None):
        a, b = self.p(x0, y1), self.p(x1, y0)
        rp = r * 0.5 * (self.kx() + self.ky())
        self.dc.rounded_rectangle([a, b], radius=rp, fill=col)
        if mr:
            self.dm.rounded_rectangle([a, b], radius=rp, fill=mr)
        if em is not None and self.de:
            self.de.rounded_rectangle([a, b], radius=rp, fill=em)

    def radial(self, cx, cy, r, inner, outer, mr, steps=16, ry_scale=1.0, em=None):
        for k in range(steps, 0, -1):
            t = k / steps
            c = tuple(int(outer[i] * t + inner[i] * (1 - t)) for i in range(3))
            self.ellipse(cx, cy, r * t, r * t * ry_scale, c, mr, em)

    def text(self, cx, cy, height, s, col, mr=None, font=FONT_BOLD, width=None):
        f = ImageFont.truetype(font, 240)
        box = f.getbbox(s)
        mask = Image.new("L", (box[2] - box[0] + 8, box[3] - box[1] + 8), 0)
        ImageDraw.Draw(mask).text((4 - box[0], 4 - box[1]), s, font=f, fill=255)
        th = max(2, int(round(height * self.ky())))
        phys_w = width if width else height * mask.width / mask.height
        tw = max(2, int(round(phys_w * self.kx())))
        mask = mask.resize((tw, th), Image.LANCZOS)
        x, y = self.p(cx, cy)
        pos = (int(x - tw / 2), int(y - th / 2))
        self.col.paste(Image.new("RGB", (tw, th), col), pos, mask)
        if mr:
            self.mr.paste(Image.new("RGB", (tw, th), mr), pos, mask)

    def finish(self):
        size = (self.w, self.h)
        out = [self.col.resize(size, Image.LANCZOS), self.mr.resize(size, Image.LANCZOS)]
        if self.em is not None:
            out.append(self.em.resize(size, Image.LANCZOS))
        return tuple(out)


def opel_logo(p: Painter, cx, cy, r, inner=BLACK, inner_mr=BLACK_MR):
    """Emblema Opel: inel cromat cu fulgerul (Blitz) orizontal."""
    p.ring(cx, cy, r, r * 0.84, CHROME, CHROME_MR, inner, inner_mr)
    k = r * 0.84
    bolt = [(-1.0, 0.03), (-1.0, 0.14), (0.30, 0.14), (0.07, -0.03), (1.0, -0.03),
            (1.0, -0.14), (-0.30, -0.14), (-0.07, 0.03)]
    p.poly([(cx + u * k, cy + v * k) for u, v in bolt], CHROME, CHROME_MR)


def plate(p: Painter, cx, cy, text, w=0.52, h=0.11):
    """Numar de inmatriculare UE 520 x 110 mm, cu banda albastra RO."""
    p.rrect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 0.006, (20, 20, 20), (0, 120, 0))
    p.rrect(cx - w / 2 + 0.004, cy - h / 2 + 0.004, cx + w / 2 - 0.004, cy + h / 2 - 0.004, 0.004,
            (238, 238, 232), (0, 90, 0))
    band = 0.042
    p.rrect(cx - w / 2 + 0.004, cy - h / 2 + 0.004, cx - w / 2 + 0.004 + band, cy + h / 2 - 0.004, 0.003,
            (16, 52, 150), (0, 90, 0))
    p.text(cx - w / 2 + 0.004 + band / 2, cy - 0.026, 0.020, "RO", (240, 240, 240), None)
    for k in range(12):
        ang = 2 * math.pi * k / 12
        p.circle(cx - w / 2 + 0.004 + band / 2 + 0.012 * math.cos(ang), cy + 0.018 + 0.012 * math.sin(ang),
                 0.0018, (250, 210, 30))
    p.text(cx + band / 2, cy, 0.075, text, (12, 12, 12), None, width=w - band - 0.06)


# ----------------------------------------------------------------------------- flancuri
def dlo_top(x):
    """Marginea de sus a ramei geamurilor laterale (stalpul A ramane vopsit)."""
    blend = float(np.clip((x - 0.15) / 0.20, 0.0, 1.0))
    return min(g.Y_RE(x), g.Y_RE(x + 0.065 * blend))


def side_texture(right: bool):
    """Un flanc, 2048 x 512, proiectie X-Y. right = partea dreapta (bușonul de rezervor)."""
    from caroserie import SIDE_X, SIDE_Y
    p = Painter(2048, 512, SIDE_X, SIDE_Y)

    xs = np.linspace(-1.88, 1.06, 400)
    belt = [g.Y_BELT(x) for x in xs]
    top = [dlo_top(x) for x in xs]

    # rama neagra a geamurilor (DLO)
    rear_edge = lambda y: -1.878 + 0.085 * (y - g.Y_BELT(-1.87)) / (g.Y_RE(-1.80) - g.Y_BELT(-1.87))
    poly = []
    for x, b in zip(xs, belt):
        poly.append((x, b - 0.004))
    for x, t in reversed(list(zip(xs, top))):
        if t > g.Y_BELT(x):
            poly.append((x, t))
    poly = [(max(x, rear_edge(y)), y) for x, y in poly]
    p.poly(poly, BLACK, BLACK_MR)

    def pane(x_front, x_back, inset=0.016, slant_back=False):
        pts = []
        for x in np.linspace(x_back, x_front, 120):
            pts.append((x, g.Y_BELT(x) + inset))
        for x in np.linspace(x_front, x_back, 120):
            pts.append((x, min(dlo_top(x), g.Y_RE(x)) - inset))
        if slant_back:
            pts = [(max(x, rear_edge(y) + inset), y) for x, y in pts]
        pts = [(x, y) for x, y in pts if y >= g.Y_BELT(x) + inset - 1e-9]
        p.poly(pts, GLASS, GLASS_MR)

    # geamul fix triunghiular / suportul oglinzii ramane negru (x > 0.85)
    pane(0.850, 0.045)
    pane(-0.045, -0.700)
    pane(-0.722, -0.858)
    pane(-0.945, -1.95, slant_back=True)

    # rosturi usi
    gap_w = 0.0045
    sill = 0.292
    p.line([(0.945, sill), (0.945, g.Y_BELT(0.945) - 0.002)], gap_w, GAP, GAP_MR)
    p.line([(0.000, sill), (0.000, g.Y_BELT(0.0) - 0.002)], gap_w, GAP, GAP_MR)
    p.line([(-0.935, sill), (-0.935, g.Y_BELT(-0.935) - 0.002)], gap_w, GAP, GAP_MR)
    p.line([(-0.935, sill), (0.945, sill)], gap_w, GAP, GAP_MR)

    # nervura laterala joasa (lumina sus, umbra jos)
    light = tuple(min(255, c + 22) for c in PAINT)
    dark = tuple(max(0, c - 34) for c in PAINT)
    p.line([(-0.90, 0.512), (0.92, 0.497)], 0.006, light)
    p.line([(-0.90, 0.503), (0.92, 0.488)], 0.007, dark)
    # umbra sub nervura de umar
    p.line([(-1.95, g.Y_SH(-1.95) - 0.012), (1.80, g.Y_SH(1.80) - 0.012)], 0.005,
           tuple(max(0, c - 18) for c in PAINT))

    # adancituri manere
    for x0, x1 in ((0.055, 0.215), (-0.835, -0.675)):
        p.ellipse((x0 + x1) / 2, 0.925, (x1 - x0) / 2 + 0.012, 0.028, dark)

    # lampa de semnalizare laterala pe aripa fata
    p.ellipse(1.045, 0.865, 0.026, 0.011, (40, 40, 40), BLACK_MR)
    p.ellipse(1.045, 0.865, 0.022, 0.008, (222, 200, 170), CLEAR_MR)

    # busonul rezervorului (dreapta, Astra H)
    if right:
        p.rrect(-1.865, 0.790, -1.700, 0.925, 0.03, GAP, GAP_MR)
        p.rrect(-1.861, 0.794, -1.704, 0.921, 0.028, PAINT, PAINT_MR)
    return p.finish()


def side_textures():
    rc, rm = side_texture(True)
    lc, lm = side_texture(False)
    col = Image.new("RGB", (2048, 1024))
    mr = Image.new("RGB", (2048, 1024))
    col.paste(rc, (0, 0)); col.paste(lc, (0, 512))
    mr.paste(rm, (0, 0)); mr.paste(lm, (0, 512))
    return col, mr


# ----------------------------------------------------------------------------- fata
def front_texture(body: g.Body, plate_text: str):
    from caroserie import FRONT_Y
    A = body.arc_nose
    p = Painter(2048, 1024, (-A, A), FRONT_Y, emissive=True)
    st = [body.stations[i] for i in range(body.i_f0, len(body.stations))]
    arcs = np.array([s["arc"] for s in st])[::-1]
    xs = np.array([s["x"] for s in st])[::-1]
    belt = lambda a: g.Y_BELT(float(np.interp(abs(a), arcs, xs)))

    for side in (-1, 1):
        S = lambda pts: [(side * a, y) for a, y in pts]
        # far: carcasa fumurie cu lentila clara
        outline = [(0.335, 0.672)]
        for a in np.linspace(0.335, 0.93, 40):
            outline.append((a, belt(a) - 0.010))
        outline += [(0.958, belt(0.958) - 0.035), (0.950, belt(0.950) - 0.075), (0.90, 0.800),
                    (0.80, 0.742), (0.68, 0.700), (0.55, 0.672), (0.42, 0.662)]
        p.poly(S([(a - 0.006, y - 0.006) for a, y in outline]), GAP, GAP_MR)
        p.poly(S(outline), (44, 46, 50), (255, 40, 200), em=(70, 0, 0))
        # proiectorul principal cu inel cromat
        cx = 0.470
        cy = 0.752
        p.radial(side * cx, cy, 0.068, (214, 216, 220), (120, 124, 130), CHROME_MR)
        p.circle(side * cx, cy, 0.055, (30, 32, 36), (255, 20, 120))
        p.radial(side * cx, cy, 0.044, (250, 250, 252), (150, 156, 166), (255, 12, 30), em=(255, 0, 0))
        p.circle(side * cx, cy, 0.020, (60, 66, 76), (255, 10, 0))
        # faza lunga si pozitie: doua reflectoare rotunde spre exterior
        for a, y, r in ((0.615, 0.742, 0.036), (0.728, 0.784, 0.031)):
            p.radial(side * a, y, r, (232, 234, 238), (140, 144, 150), CHROME_MR, em=(150, 0, 0))
            p.circle(side * a, y, r * 0.45, (200, 205, 214), (255, 15, 40), em=(255, 0, 0))
        # semnalizarea: banda clara-chihlimbar sus, spre aripa
        p.poly(S([(0.76, belt(0.76) - 0.020), (0.92, belt(0.92) - 0.020), (0.935, belt(0.935) - 0.040),
                  (0.80, belt(0.80) - 0.042)]), (214, 168, 96), (255, 25, 20), em=(0, 255, 0))

        # proiectoare de ceata in nisa neagra
        lo, hi = sorted([side * 0.48, side * 0.79])
        p.rrect(lo, 0.300, hi, 0.445, 0.035, PLASTIC, PLASTIC_MR)
        for k in range(5):
            y = 0.312 + k * 0.028
            p.line(S([(0.50, y), (0.77, y)]), 0.004, (18, 18, 19))
        p.radial(side * 0.645, 0.372, 0.046, (90, 92, 96), (30, 30, 32), BLACK_MR)
        p.radial(side * 0.645, 0.372, 0.036, (246, 246, 248), (150, 152, 158), CHROME_MR, em=(200, 0, 0))

    # grila superioara: trapez negru cu lamele si bara cromata cu emblema
    top_y = belt(0.0) - 0.014
    grille = [(-0.322, top_y), (0.322, top_y), (0.305, 0.740), (0.278, 0.668), (-0.278, 0.668),
              (-0.305, 0.740)]
    p.poly([(a * 1.03, y + (0.004 if y > 0.74 else -0.004)) for a, y in grille], GAP, GAP_MR)
    p.poly(grille, PLASTIC, PLASTIC_MR)
    for y in (0.752, 0.726, 0.700):
        w = 0.278 + (y - 0.668) / 0.072 * 0.027
        p.line([(-w + 0.01, y), (w - 0.01, y)], 0.008, (70, 72, 76), (255, 60, 200))
    p.poly([(-0.322, 0.814), (0.322, 0.814), (0.316, 0.788), (-0.316, 0.788)], CHROME, CHROME_MR)
    opel_logo(p, 0.0, 0.778, 0.056)

    # numarul de inmatriculare
    plate(p, *FRONT_PLATE, plate_text)

    # grila inferioara (priza de aer), lamele orizontale si rama cromata subtire
    lower = [(-0.405, 0.432), (0.405, 0.432), (0.355, 0.285), (-0.355, 0.285)]
    p.poly([(a * 1.02, y + (0.004 if y > 0.4 else -0.004)) for a, y in lower], CHROME, CHROME_MR)
    p.poly(lower, PLASTIC, PLASTIC_MR)
    for k in range(5):
        y = 0.305 + k * 0.027
        w = 0.355 + (y - 0.285) / 0.147 * 0.05
        p.line([(-w + 0.012, y), (w - 0.012, y)], 0.006, (64, 66, 70), (0, 120, 60))
    # spoilerul inferior negru
    p.poly([(-0.95, 0.16), (0.95, 0.16), (0.95, 0.245), (0.40, 0.262), (-0.40, 0.262), (-0.95, 0.245)],
           PLASTIC, PLASTIC_MR)
    return p.finish()


# ----------------------------------------------------------------------------- spate
def rear_texture(body: g.Body, plate_text: str):
    from caroserie import REAR_Y
    A = body.arc_rear
    p = Painter(2048, 1024, (-A, A), REAR_Y, emissive=True)

    # luneta cu serigrafie neagra pe margine
    p.rrect(-0.535, 0.985, 0.535, 1.352, 0.05, BLACK, BLACK_MR)
    p.rrect(-0.505, 1.012, 0.505, 1.326, 0.04, GLASS, GLASS_MR)
    p.rrect(-0.14, 1.330, 0.14, 1.346, 0.006, (120, 8, 12), RED_MR, em=(255, 0, 0))  # stop pe plafon
    for k in range(12):                                                    # rezistenta dezaburire
        y = 1.04 + k * 0.022
        p.line([(-0.46, y), (0.46, y)], 0.0012, (40, 34, 30))

    for side in (-1, 1):
        S = lambda pts: [(side * a, y) for a, y in pts]
        # rostul haionului
        p.line(S([(0.548, 1.372), (0.548, 0.620)]), 0.0045, GAP, GAP_MR)
        # stopurile verticale de pe stalpii D
        outline = [(0.566, 0.800), (0.566, 1.230), (0.600, 1.262), (0.700, 1.262), (0.790, 1.205),
                   (0.815, 1.000), (0.810, 0.800)]
        p.poly(S([(a + (0.005 if a > 0.6 else -0.005), y + (0.005 if y > 1 else -0.005)) for a, y in outline]),
               GAP, GAP_MR)
        p.poly(S(outline), RED, RED_MR, em=(255, 0, 0))
        p.poly(S([(0.566, 0.985), (0.813, 0.985), (0.812, 1.075), (0.566, 1.075)]), CLEAR, CLEAR_MR, em=(0, 0, 0))
        p.circle(side * 0.640, 1.030, 0.026, (225, 150, 60), (255, 20, 40), em=(0, 255, 0))  # semnalizare
        p.circle(side * 0.740, 1.030, 0.024, (232, 234, 238), CHROME_MR)      # marsarier
        for y in (0.86, 0.90, 0.94, 1.14, 1.18):
            p.line(S([(0.575, y), (0.80, y)]), 0.003, (190, 24, 30))
        # catadioptrii din bara
        lo, hi = sorted([side * 0.62, side * 0.76])
        p.rrect(lo, 0.430, hi, 0.455, 0.006, (120, 10, 14), RED_MR)

    # bara spate: rost sus, zona inferioara neagra
    p.line([(-0.97, 0.603), (0.97, 0.603)], 0.0045, GAP, GAP_MR)
    p.line([(-0.548, 0.620), (0.548, 0.620)], 0.0045, GAP, GAP_MR)
    p.poly([(-0.96, 0.22), (0.96, 0.22), (0.96, 0.350), (0.55, 0.372), (-0.55, 0.372), (-0.96, 0.350)],
           PLASTIC, PLASTIC_MR)

    # nisa numarului, maner cromat, emblema, inscriptie
    p.rrect(-0.292, 0.628, 0.292, 0.768, 0.02, tuple(c - 24 for c in PAINT), PAINT_MR)
    plate(p, *REAR_PLATE, plate_text)
    p.rrect(-0.225, 0.776, 0.225, 0.792, 0.006, CHROME, CHROME_MR)
    opel_logo(p, 0.0, 0.862, 0.046)
    p.text(0.360, 0.930, 0.024, "ASTRA", CHROME, CHROME_MR, font=FONT_BOLD)
    return p.finish()


# ----------------------------------------------------------------------------- anvelopa
def tire_textures(v_tread=(0.35, 0.65), w_tread=(-0.060, 0.060)):
    W, H = 2048, 512
    height = np.ones((H, W), np.float32)
    v = (np.arange(H) + 0.5) / H

    def v_of(w):
        return v_tread[0] + (w - w_tread[0]) / (w_tread[1] - w_tread[0]) * (v_tread[1] - v_tread[0])

    # 4 santuri circumferentiale
    for w in (-0.040, -0.014, 0.014, 0.040):
        c, hw = v_of(w), 0.0045 / (w_tread[1] - w_tread[0]) * (v_tread[1] - v_tread[0])
        height[np.abs(v - c) < hw, :] = 0.0
    # lamele transversale pe umeri si nervurile exterioare
    pitch = 1.0 / 74
    for side in (-1, 1):
        v_a, v_b = sorted([v_of(side * 0.040), v_of(side * 0.068)])
        r = np.nonzero((v > v_a) & (v < v_b))[0]
        for k in range(74):
            u0 = k * pitch + (0.25 * pitch if side > 0 else 0)
            for du in range(-3, 4):
                cols = (u0 * W + du + side * 0.4 * (r - r[0])).astype(int) % W
                height[r, cols] = 0.0
        v_a, v_b = sorted([v_of(side * 0.014), v_of(side * 0.040)])
        rows = (v > v_a) & (v < v_b)
        for k in range(74):
            col = int((k * pitch + 0.5 * pitch) * W) % W
            height[rows, col:col + 2] = 0.35

    img_h = Image.fromarray((height * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    h = np.asarray(img_h, np.float32) / 255.0
    base = np.where(h[..., None] > 0.5, np.array([30, 30, 32]), np.array([14, 14, 15])).astype(np.float32)
    base = base * (0.94 + 0.06 * np.random.default_rng(1).random((H, W, 1)))
    color = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))

    # inscriptii pe flancul exterior (v mare = exterior)
    d = ImageDraw.Draw(color)
    font = ImageFont.truetype(FONT_BOLD, 26)
    for k, s in enumerate(("205/55 R16 91V", "TUBELESS", "205/55 R16 91V", "M+S")):
        d.text((60 + k * 512, int(0.875 * H) - 14), s, font=font, fill=(52, 52, 55))

    # normale din harta de inaltime
    hx = np.roll(h, -1, 1) - np.roll(h, 1, 1)
    hy = np.roll(h, -1, 0) - np.roll(h, 1, 0)
    k = 2.0
    n = np.dstack([-hx * k, hy * k, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    normal = Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8))
    mr = Image.fromarray(np.dstack([np.zeros_like(h), 0.80 + 0.12 * (1 - h), np.zeros_like(h)])
                         .__mul__(255).astype(np.uint8))
    return color, mr, normal


def cap_texture():
    p = Painter(256, 256, (-1, 1), (-1, 1), base=(26, 26, 28), base_mr=(255, 60, 120), ss=4)
    p.circle(0, 0, 1.0, (150, 154, 158), CHROME_MR)
    p.circle(0, 0, 0.90, (24, 24, 26), BLACK_MR)
    opel_logo(p, 0.0, 0.0, 0.78)
    return p.finish()


def encode(img: Image.Image, kind="jpeg", quality=90) -> tuple[bytes, str]:
    buf = io.BytesIO()
    if kind == "webp":
        img.convert("RGB").save(buf, "WEBP", quality=quality, method=6)
        return buf.getvalue(), "image/webp"
    if kind == "webp_lossless":
        img.convert("RGB").save(buf, "WEBP", lossless=True, method=6)
        return buf.getvalue(), "image/webp"
    if kind == "jpeg":
        img.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True, subsampling=0)
        return buf.getvalue(), "image/jpeg"
    img.save(buf, "PNG", optimize=True)
    return buf.getvalue(), "image/png"

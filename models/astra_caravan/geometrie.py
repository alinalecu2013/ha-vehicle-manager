"""Geometria Opel Astra H Caravan (A04, 2004-2010) la cote reale.

Sistem de axe (glTF): X spre fata, Y in sus, Z spre dreapta masinii; solul la Y = 0.
Originea pe X este la mijlocul ampatamentului, pe Z in planul de simetrie.

Cote oficiale (auto-data.net, ADAC, fisa tehnica Opel):
  lungime 4515 mm, latime 1794 mm (fara oglinzi), inaltime 1500 mm (cu bare de plafon),
  ampatament 2703 mm, ecartament 1488 / 1488 mm, consola fata 871 mm, spate 941 mm,
  garda la sol 160 mm, anvelope 205/55 R16.

Caroseria este o singura suprafata-grila: statii transversale de la spate la fata, fiecare
statie fiind un inel cu acelasi numar de puncte. La capete inelele se ingusteaza pana la zero
(ca polii unei sfere), astfel ca fata si spatele sunt tot zone ale grilei si pot primi
texturi desfasurate (faruri, grila, stopuri).
"""

from __future__ import annotations

import math

import numpy as np

# ----------------------------------------------------------------------------- cote
LENGTH = 4.515
WIDTH = 1.794
HEIGHT = 1.500
WHEELBASE = 2.703
TRACK = 1.488
OVERHANG_F = 0.871
OVERHANG_R = 0.941
CLEARANCE = 0.160

AXLE_F = WHEELBASE / 2.0
AXLE_R = -WHEELBASE / 2.0
X_NOSE = AXLE_F + OVERHANG_F          # 2.2225
X_TAIL = AXLE_R - OVERHANG_R          # -2.2925
HW = WIDTH / 2.0

TIRE_R = (16 * 25.4 + 2 * 0.55 * 205) / 2000.0   # 205/55 R16 -> 0.316 m
TIRE_W = 0.205
RIM_R = 16 * 25.4 / 2000.0                       # 0.2032 m
WHEEL_Y = TIRE_R
WHEEL_Z = TRACK / 2.0
ARCH_R = 0.385                                   # raza decupajului aripii

X_F0 = 1.90        # de aici incepe rotunjirea botului (in plan)
X_R0 = -2.13       # de aici incepe rotunjirea spatelui
NOSE_N = 2.4       # exponent superelipsa in plan (mai mic = mai rotund)
TAIL_N = 3.6

# Randuri pe jumatate de inel: A = podea, B = flanc, C = geamuri / aripa, D = plafon / capota
N_A, N_B, N_C, N_D = 6, 40, 22, 22
HALF = N_A + N_B + N_C + N_D
RING = 2 * HALF
ROW_B, ROW_C, ROW_D = N_A, N_A + N_B, N_A + N_B + N_C

STEP_MID = 0.018
N_NOSE = 44
N_TAILS = 30


# ----------------------------------------------------------------------------- interpolare
class Pchip:
    """Interpolare cubica monotona (Fritsch-Carlson): fara oscilatii intre puncte."""

    def __init__(self, points):
        pts = sorted(points)
        self.x = np.array([p[0] for p in pts], float)
        self.y = np.array([p[1] for p in pts], float)
        h = np.diff(self.x)
        d = np.diff(self.y) / h
        m = np.zeros_like(self.x)
        m[0], m[-1] = d[0], d[-1]
        for k in range(1, len(self.x) - 1):
            if d[k - 1] * d[k] <= 0:
                m[k] = 0.0
            else:
                w1, w2 = 2 * h[k] + h[k - 1], h[k] + 2 * h[k - 1]
                m[k] = (w1 + w2) / (w1 / d[k - 1] + w2 / d[k])
        self.m = m

    def __call__(self, x):
        x = float(np.clip(x, self.x[0], self.x[-1]))
        k = int(np.clip(np.searchsorted(self.x, x) - 1, 0, len(self.x) - 2))
        h = self.x[k + 1] - self.x[k]
        t = (x - self.x[k]) / h
        h00, h10 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t
        h01, h11 = -2 * t**3 + 3 * t**2, t**3 - t**2
        return float(h00 * self.y[k] + h10 * h * self.m[k] + h01 * self.y[k + 1] + h11 * h * self.m[k + 1])


# ----------------------------------------------------------------------------- profile (x -> valoare)
# Latimea maxima (semi), cea mai mare la arcade: 1794 / 2 = 0.897 m.
HW_MAX = Pchip([(X_TAIL, 0.875), (X_R0, 0.884), (-1.80, 0.894), (AXLE_R, HW), (-0.60, 0.891),
                (0.30, 0.891), (AXLE_F, HW), (1.70, 0.893), (X_F0, 0.884), (X_NOSE, 0.86)])
# Marginea inferioara a caroseriei (praguri, bare).
Y_BOT = Pchip([(X_TAIL, 0.300), (-2.00, 0.270), (-1.75, 0.235), (-0.98, 0.215),
               (0.98, 0.215), (1.75, 0.222), (2.00, 0.215), (X_NOSE, 0.205)])
# Nervura de umar (sub linia geamurilor).
Y_SH = Pchip([(X_TAIL, 0.935), (-1.50, 0.925), (0.00, 0.905), (1.00, 0.885), (1.60, 0.862),
              (1.90, 0.845), (X_NOSE, 0.800)])
# Linia de centura: baza geamurilor; pe capota = muchia aripii.
Y_BELT = Pchip([(X_TAIL, 1.050), (-1.85, 1.045), (-1.00, 1.025), (0.00, 1.005), (0.50, 0.995),
                (0.95, 0.985), (1.07, 0.968), (1.20, 0.950), (1.60, 0.920), (2.00, 0.890),
                (X_NOSE, 0.850)])
# Muchia plafonului (sus pe geamuri); intre 0.25 si 1.07 este stalpul A.
Y_RE = Pchip([(X_TAIL, 1.368), (X_R0, 1.375), (-1.80, 1.390), (-1.00, 1.405), (0.00, 1.410),
              (0.22, 1.405), (0.35, 1.380), (0.55, 1.290), (0.80, 1.140), (1.07, 0.990),
              (1.20, 0.972), (1.60, 0.945), (2.00, 0.910), (X_NOSE, 0.868)])
# Axa centrala sus: capota, parbriz, plafon (fara bare).
Y_TOP = Pchip([(X_TAIL, 1.418), (X_R0, 1.425), (-1.80, 1.435), (-1.00, 1.445), (0.00, 1.448),
               (0.20, 1.440), (0.35, 1.410), (0.55, 1.315), (0.80, 1.170), (1.07, 1.010),
               (1.20, 0.995), (1.60, 0.968), (2.00, 0.932), (X_NOSE, 0.884)])
HW_BELT = Pchip([(X_TAIL, 0.840), (-1.50, 0.852), (0.00, 0.852), (0.90, 0.850), (1.07, 0.845),
                 (1.60, 0.845), (X_NOSE, 0.820)])
HW_RE = Pchip([(X_TAIL, 0.615), (-1.50, 0.640), (0.00, 0.650), (0.25, 0.650), (0.60, 0.675),
               (0.90, 0.725), (1.07, 0.770), (1.30, 0.772), (2.00, 0.760), (X_NOSE, 0.750)])

WINDSHIELD = (0.25, 1.07)     # parbrizul, intre plafon si torpedou
COWL = (1.035, 1.10)          # grila de sub stergatoare


def front_shear(y: float) -> float:
    """Retragerea fetei pe X in functie de inaltime: capota urca spre spate, bara se ascunde jos."""
    top = max(0.0, (y - 0.50) / 0.36)
    low = max(0.0, (0.36 - y) / 0.15)
    return -0.175 * min(top, 1.15) ** 1.5 - 0.060 * min(low, 1.0) ** 1.5


def rear_shear(y: float) -> float:
    """Hayonul se inclina spre fata; bara spate iese peste el."""
    low = max(0.0, (0.36 - y) / 0.10)
    step = np.clip((y - 0.56) / 0.06, 0.0, 1.0)
    step = step * step * (3 - 2 * step)
    lean = max(0.0, (y - 0.62) / 0.80)
    return 0.040 * min(low, 1.0) ** 1.5 + 0.045 * step + 0.150 * lean**1.2


# ----------------------------------------------------------------------------- curbe 2D
def catmull_rom(points, per_span=24):
    p = np.asarray(points, float)
    p = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    out = []
    for k in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[k - 1], p[k], p[k + 1], p[k + 2]
        for t in np.linspace(0, 1, per_span, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(p[-2])
    return np.array(out)


def bezier(ctrl, n=200):
    c = np.asarray(ctrl, float)
    t = np.linspace(0, 1, n)[:, None]
    if len(c) == 3:
        return (1 - t) ** 2 * c[0] + 2 * (1 - t) * t * c[1] + t**2 * c[2]
    return (1 - t) ** 3 * c[0] + 3 * (1 - t) ** 2 * t * c[1] + 3 * (1 - t) * t**2 * c[2] + t**3 * c[3]


def resample(poly, targets):
    """Puncte pe polilinie la distantele (lungime de arc) date, ca fractii 0..1."""
    seg = np.linalg.norm(np.diff(poly, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    total = cum[-1]
    out = []
    for f in targets:
        s = f * total
        k = int(np.clip(np.searchsorted(cum, s) - 1, 0, len(seg) - 1))
        t = 0.0 if seg[k] < 1e-12 else (s - cum[k]) / seg[k]
        out.append(poly[k] + t * (poly[k + 1] - poly[k]))
    return np.array(out), total


def half_section(x_h: float, x_w: float, scale: float = 1.0) -> np.ndarray:
    """Jumatatea +Z a inelului: (HALF + 1) puncte (z, y) de la podea la axa de sus.

    Inaltimile vin din profilele la x_h; latimile de la x_w, inmultite cu scale (capete).
    """
    hw, hwb, hwr = HW_MAX(x_w), HW_BELT(x_w), HW_RE(x_w)
    yb, ysh, ybelt, yre, ytop = Y_BOT(x_h), Y_SH(x_h), Y_BELT(x_h), Y_RE(x_h), Y_TOP(x_h)
    ybelt = min(ybelt, yre - 0.004)
    ysh = min(ysh, ybelt - 0.025)
    ytop = max(ytop, yre + 0.006)

    # A: podeaua, usor coborata spre centru (garda la sol 160 mm)
    y_floor = max(CLEARANCE, yb - 0.055)
    zA = np.linspace(0, hw - 0.075, N_A + 1)
    yA = y_floor + (yb - y_floor) * (zA / zA[-1]) ** 2
    seg_a = np.column_stack([zA, yA])

    # B: prag, flanc bombat, nervura de umar, pana la centura
    ctrl = [(hw - 0.075, yb), (hw - 0.030, yb + 0.018), (hw - 0.010, yb + 0.075),
            (hw - 0.002, yb + 0.20), (hw, 0.5 * (yb + ysh) + 0.04), (hw - 0.004, ysh - 0.03),
            (hw - 0.012, ysh), (hwb, ybelt)]
    seg_b, _ = resample(catmull_rom(ctrl), np.linspace(0, 1, N_B + 1))

    # C: geamul lateral (sau rotunjirea aripii pe capota), usor convex
    c1 = (hwb - 0.22 * (hwb - hwr), ybelt + 0.62 * (yre - ybelt))
    seg_c, _ = resample(bezier([(hwb, ybelt), c1, (hwr, yre)]), np.linspace(0, 1, N_C + 1))

    # D: muchia plafonului / capotei si suprafata de sus pana la axa
    dy = ytop - yre
    curve = bezier([(hwr, yre), (hwr - 0.012, yre + 0.65 * dy), (0.52 * hwr, ytop), (0, ytop)], 400)
    _, total = resample(curve, [0, 1])
    first = min(0.006 / total, 0.05)        # randul ingust = rost de capota / ornament negru
    targets = np.concatenate([[0, first], np.linspace(first, 1, N_D)[1:]])
    seg_d, _ = resample(curve, targets)

    half = np.vstack([seg_a, seg_b[1:], seg_c[1:], seg_d[1:]])
    half[:, 0] *= scale
    half[-1, 0] = 0.0
    return half


def end_curve(x0: float, depth: float, n_exp: float, count: int, sign: int):
    """Statii pe rotunjirea in plan a unui capat: (x, scara latimii, arc de la centru)."""
    th = np.linspace(0, math.pi / 2, 4000)
    xf = np.sin(th) ** (2 / n_exp)
    cf = np.cos(th) ** (2 / n_exp)
    hw0 = HW_MAX(x0)
    pts = np.column_stack([x0 + sign * depth * xf, hw0 * cf])
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cum = np.concatenate([[0], np.cumsum(seg)])
    total = cum[-1]
    out = []
    for s in np.linspace(0, total, count + 1)[1:]:    # fara statia de start (este in zona mijlocie)
        k = int(np.clip(np.searchsorted(cum, s), 1, len(cum) - 1))
        t = (s - cum[k - 1]) / max(cum[k] - cum[k - 1], 1e-12)
        x = pts[k - 1, 0] + t * (pts[k, 0] - pts[k - 1, 0])
        c = (cf[k - 1] + t * (cf[k] - cf[k - 1]))
        xfrac = abs(x - x0) / depth
        out.append((x, c, total - s, xfrac))
    out[-1] = (x0 + sign * depth, 0.0, 0.0, 1.0)
    return out, total


# ----------------------------------------------------------------------------- caroseria
class Body:
    """Grila caroseriei: P[statie, inel] plus etichete pentru materiale si UV."""

    def __init__(self):
        rear, self.arc_rear = end_curve(X_R0, X_R0 - X_TAIL, TAIL_N, N_TAILS, -1)
        nose, self.arc_nose = end_curve(X_F0, X_NOSE - X_F0, NOSE_N, N_NOSE, +1)
        mid = np.linspace(X_R0, X_F0, int(round((X_F0 - X_R0) / STEP_MID)) + 1)

        stations = []
        for x, c, a, xf in reversed(rear):
            stations.append(dict(x=x, region="rear", scale=c, arc=a, w=_smooth(xf)))
        for x in mid:
            stations.append(dict(x=float(x), region="mid", scale=1.0, arc=None, w=0.0))
        for x, c, a, xf in nose:
            stations.append(dict(x=x, region="nose", scale=c, arc=a, w=_smooth(xf)))
        # capetele zonei mijlocii sunt si inceputul desfasurarii fata / spate
        self.i_r0 = len(rear)
        self.i_f0 = len(rear) + len(mid) - 1
        stations[self.i_r0]["arc"] = self.arc_rear
        stations[self.i_f0]["arc"] = self.arc_nose
        self.stations = stations

        ns = len(stations)
        P = np.zeros((ns, RING, 3))
        X0 = np.zeros((ns, RING))
        for i, st in enumerate(stations):
            x = st["x"]
            if st["region"] == "rear":
                half = half_section(x, X_R0, st["scale"])
            elif st["region"] == "nose":
                half = half_section(x, X_F0, st["scale"])
            else:
                half = half_section(x, x)
            ring = np.vstack([half, half[-2:0:-1] * [-1, 1]])
            ys = ring[:, 1]
            if st["region"] == "nose":
                dx = np.array([front_shear(y) for y in ys]) * st["w"]
            elif st["region"] == "rear":
                dx = np.array([rear_shear(y) for y in ys]) * st["w"]
            else:
                dx = np.zeros(RING)
            P[i, :, 0] = x + dx
            P[i, :, 1] = ys
            P[i, :, 2] = ring[:, 0]
            X0[i, :] = x
        self.P, self.X0 = P, X0
        self.removed = np.zeros((ns - 1, RING), bool)
        self._cut_arches()

    # -- decupajele pentru roti --------------------------------------------------
    def _cut_arches(self):
        P = self.P
        rows = np.array([seg_of(j) in "AB" for j in range(RING)])
        inside = np.zeros(P.shape[:2], bool)
        for xa in (AXLE_F, AXLE_R):
            for i, st in enumerate(self.stations):
                if st["region"] != "mid":
                    continue
                for j in np.nonzero(rows)[0]:
                    x, y, z = P[i, j]
                    if abs(z) < 0.58:
                        continue
                    dx, dy = x - xa, y - WHEEL_Y
                    d = math.hypot(dx, dy)
                    if d >= ARCH_R:
                        continue
                    inside[i, j] = True
                    if y >= WHEEL_Y:
                        P[i, j, 0] = xa + dx / d * ARCH_R
                        P[i, j, 1] = WHEEL_Y + dy / d * ARCH_R
                    else:
                        half = math.sqrt(max(ARCH_R**2 - dy**2, 0.0))
                        P[i, j, 0] = xa + (half if dx >= 0 else -half)
        nxt = (np.arange(RING) + 1) % RING
        self.removed = inside[:-1, :] & inside[1:, :] & inside[:-1, nxt] & inside[1:, nxt]

    # -- interogari ----------------------------------------------------------------
    def x_of(self, i):
        return self.stations[i]["x"]

    def region(self, i):
        return self.stations[i]["region"]


def _smooth(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def seg_of(j: int) -> str:
    """Segmentul (A/B/C/D) caruia ii apartine randul j al inelului (simetric)."""
    k = j if j <= HALF else RING - j
    if k < ROW_B:
        return "A"
    if k < ROW_C:
        return "B"
    if k < ROW_D:
        return "C"
    return "D"


def row_in_d(j: int) -> int:
    """Al catelea rand in segmentul D (0 = randul ingust de la muchie)."""
    k = j if j < HALF else RING - j - 1
    return k - ROW_D


def quad_seg(j: int) -> str:
    """Segmentul unui quad (intre randurile j si j+1)."""
    k = j if j < HALF else RING - 1 - j
    if k < ROW_B:
        return "A"
    if k < ROW_C:
        return "B"
    if k < ROW_D:
        return "C"
    return "D"

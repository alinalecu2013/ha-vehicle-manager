"""Piese atasate caroseriei: roti (anvelopa, janta 16", frana), oglinzi, manere, bare de plafon,
stergatoare, pasaje de roata, evacuare."""

from __future__ import annotations

import math

import numpy as np

import geometrie as g
from glb import Scene, smooth_normals


def add(scene: Scene, mesh, mat, pos, faces, nrm=None, uv=None):
    pos = np.asarray(pos, float)
    faces = np.asarray(faces, np.int64)
    if nrm is None:
        nrm = smooth_normals(pos, faces)
    scene.prim(mesh, mat).add(pos, nrm, faces, uv)


# ----------------------------------------------------------------------------- interogari suprafata
def side_z(body: g.Body, x: float, y: float) -> float:
    """|z| al flancului la (x, y), din grila caroseriei."""
    i = int(np.argmin([abs(s["x"] - x) if s["region"] == "mid" else 9 for s in body.stations]))
    ring = body.P[i, g.ROW_B:g.ROW_D + 1]
    ys, zs = ring[:, 1], ring[:, 2]
    return float(np.interp(y, ys, zs))


def top_y(body: g.Body, x: float, z: float) -> float:
    """Inaltimea suprafetei de sus (plafon / parbriz / capota) la (x, |z|)."""
    i = int(np.argmin([abs(s["x"] - x) if s["region"] == "mid" else 9 for s in body.stations]))
    ring = body.P[i, g.ROW_D:g.HALF + 1]
    return float(np.interp(abs(z), ring[::-1, 2], ring[::-1, 1]))


# ----------------------------------------------------------------------------- primitive
def lathe(profile, nseg, vs=None, phase=0.0):
    """Suprafata de revolutie in jurul axei w. profile: (r, w). Normala spre stanga tangentei."""
    prof = np.asarray(profile, float)
    n = len(prof)
    th = phase + np.linspace(0, 2 * math.pi, nseg + 1)
    pos = np.zeros((n, nseg + 1, 3))
    nrm = np.zeros_like(pos)
    tang = np.gradient(prof, axis=0)
    n2 = np.column_stack([tang[:, 1], -tang[:, 0]])
    n2 /= np.linalg.norm(n2, axis=1, keepdims=True)
    for i, (r, w) in enumerate(prof):
        pos[i, :, 0] = r * np.cos(th)
        pos[i, :, 1] = r * np.sin(th)
        pos[i, :, 2] = w
        nrm[i, :, 0] = n2[i, 0] * np.cos(th)
        nrm[i, :, 1] = n2[i, 0] * np.sin(th)
        nrm[i, :, 2] = n2[i, 1]
    idx = np.arange(n * (nseg + 1)).reshape(n, nseg + 1)
    faces = []
    for i in range(n - 1):
        for k in range(nseg):
            a, b, c, d = idx[i, k], idx[i, k + 1], idx[i + 1, k + 1], idx[i + 1, k]
            faces += [(a, b, c), (a, c, d)]
    faces = np.array(faces)
    P, N = pos.reshape(-1, 3), nrm.reshape(-1, 3)
    # winding potrivit normalelor
    f = faces[0]
    fn = np.cross(P[f[1]] - P[f[0]], P[f[2]] - P[f[0]])
    if np.dot(fn, N[f[0]] + N[f[1]] + N[f[2]]) < 0:
        faces = faces[:, ::-1]
    uv = None
    if vs is not None:
        uu, vv = np.meshgrid(np.linspace(0, 1, nseg + 1), vs)
        uv = np.column_stack([uu.ravel(), vv.ravel()])
    return P, N, faces, uv


def superellipsoid(center, semi, e1=0.5, e2=0.5, nu=14, nv=28):
    cx, cy, cz = center
    a, b, c = semi
    sp = lambda v, e: np.sign(v) * np.abs(v) ** e
    us = np.linspace(-math.pi / 2, math.pi / 2, nu + 1)
    vs = np.linspace(-math.pi, math.pi, nv, endpoint=False)
    pos = []
    for u in us:
        for v in vs:
            pos.append((cx + a * sp(math.cos(u), e1) * sp(math.cos(v), e2),
                        cy + b * sp(math.sin(u), e1),
                        cz + c * sp(math.cos(u), e1) * sp(math.sin(v), e2)))
    faces = []
    for i in range(nu):
        for k in range(nv):
            a0, b0 = i * nv + k, i * nv + (k + 1) % nv
            c0, d0 = (i + 1) * nv + (k + 1) % nv, (i + 1) * nv + k
            faces += [(a0, d0, c0), (a0, c0, b0)]
    pos = np.array(pos)
    faces = np.array(faces)
    return pos, _outward(pos, faces, np.array(center))


def _outward(pos, faces, center):
    p0, p1, p2 = pos[faces[:, 0]], pos[faces[:, 1]], pos[faces[:, 2]]
    fn = np.cross(p1 - p0, p2 - p0)
    if np.einsum("ij,ij->i", fn, (p0 + p1 + p2) / 3 - center).sum() < 0:
        faces = faces[:, ::-1]
    return faces


def sweep(path, section, closed_ends=True):
    """Extrudeaza o sectiune 2D (u = lateral, v = sus) de-a lungul unei polilinii 3D."""
    path = np.asarray(path, float)
    sec = np.asarray(section, float)
    m = len(sec)
    pos = []
    for i in range(len(path)):
        t = path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]
        t /= np.linalg.norm(t)
        up = np.array([0.0, 1.0, 0.0])
        side = np.cross(t, up)
        if np.linalg.norm(side) < 1e-6:
            side = np.array([0.0, 0.0, 1.0])
        side /= np.linalg.norm(side)
        up = np.cross(side, t)
        for u, v in sec:
            pos.append(path[i] + side * u + up * v)
    faces = []
    for i in range(len(path) - 1):
        for k in range(m):
            a, b = i * m + k, i * m + (k + 1) % m
            c, d = (i + 1) * m + (k + 1) % m, (i + 1) * m + k
            faces += [(a, b, c), (a, c, d)]
    pos = np.array(pos)
    if closed_ends:
        for i, sgn in ((0, 1), (len(path) - 1, -1)):
            ci = len(pos)
            pos = np.vstack([pos, path[i]])
            for k in range(m):
                a, b = i * m + k, i * m + (k + 1) % m
                faces.append((ci, b, a) if sgn > 0 else (ci, a, b))
    faces = np.array(faces)
    # orientare: normalele laterale departe de axa
    p0, p1, p2 = pos[faces[:, 0]], pos[faces[:, 1]], pos[faces[:, 2]]
    fn = np.cross(p1 - p0, p2 - p0)
    cen = (p0 + p1 + p2) / 3
    near = np.array([path[np.argmin(np.linalg.norm(path - c, axis=1))] for c in cen[: len(path) * m * 2: 7]])
    if np.einsum("ij,ij->i", fn[: len(path) * m * 2: 7], cen[: len(path) * m * 2: 7] - near).sum() < 0:
        faces = faces[:, ::-1]
    return pos, faces


def rounded_section(hw, hh, n=16, e=0.35):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return np.column_stack([hw * np.sign(np.cos(t)) * np.abs(np.cos(t)) ** e,
                            hh * np.sign(np.sin(t)) * np.abs(np.sin(t)) ** e])


# ----------------------------------------------------------------------------- roata
TIRE_PROFILE = [  # (r, w, v)
    (0.2070, -0.0900, 0.00), (0.2200, -0.0950, 0.03), (0.2350, -0.0990, 0.06), (0.2500, -0.1015, 0.09),
    (0.2650, -0.1025, 0.12), (0.2800, -0.1015, 0.155), (0.2920, -0.0990, 0.19), (0.3010, -0.0955, 0.22),
    (0.3070, -0.0910, 0.25), (0.3115, -0.0850, 0.28), (0.3140, -0.0780, 0.31), (0.3155, -0.0690, 0.335),
    (0.3160, -0.0600, 0.35), (0.3162, -0.0300, 0.425), (0.3163, 0.0000, 0.50), (0.3162, 0.0300, 0.575),
    (0.3160, 0.0600, 0.65), (0.3155, 0.0690, 0.665), (0.3140, 0.0780, 0.69), (0.3115, 0.0850, 0.72),
    (0.3070, 0.0910, 0.75), (0.3010, 0.0955, 0.78), (0.2920, 0.0990, 0.81), (0.2800, 0.1015, 0.845),
    (0.2650, 0.1025, 0.88), (0.2500, 0.1015, 0.91), (0.2350, 0.0990, 0.94), (0.2200, 0.0950, 0.97),
    (0.2070, 0.0900, 1.00),
]

R_FACE_IN, R_FACE_OUT = 0.036, 0.193


def face_w(r):
    """Adancimea fetei jantei: spitele coboara spre butuc (janta concava)."""
    return 0.046 + (r - R_FACE_IN) / (R_FACE_OUT - R_FACE_IN) * 0.028


def wheel_parts():
    """Roata in coordonate locale (p, q, w): w spre exterior. Intoarce {material: [(pos, nrm, faces, uv)]}."""
    parts: dict[str, list] = {}

    def put(mat, pos, faces, nrm=None, uv=None):
        if nrm is None:
            nrm = smooth_normals(np.asarray(pos, float), np.asarray(faces))
        parts.setdefault(mat, []).append((np.asarray(pos, float), np.asarray(nrm, float), np.asarray(faces), uv))

    # anvelopa
    prof = [(r, w) for r, w, _ in TIRE_PROFILE]
    vs = [v for _, _, v in TIRE_PROFILE]
    P, N, F, UV = lathe(prof, 96, vs)
    put("tire", P, F, N, UV)

    # buza si umarul jantei
    lip = [(0.2040, 0.0640), (0.2110, 0.0740), (0.2140, 0.0830), (0.2130, 0.0900), (0.2085, 0.0945),
           (0.2010, 0.0940), (0.1965, 0.0870), (0.1940, 0.0790), (R_FACE_OUT, face_w(R_FACE_OUT))]
    P, N, F, _ = lathe(lip, 96)
    put("rim", P, F, N)
    # butoiul interior (vizibil printre spite), normala spre axa
    P, N, F, _ = lathe([(0.191, 0.074), (0.190, 0.020), (0.188, -0.080)], 64)
    put("rim_inner", P, F, -N)
    # scutul din spate (umbra)
    P, N, F, _ = lathe([(0.188, -0.082), (0.010, -0.082)], 48)
    put("dark", P, F, N if N[0, 2] > 0 else -N)

    # discul de frana 280 mm si butucul
    for w, sgn in ((-0.030, 1), (-0.052, -1)):
        P, N, F, _ = lathe([(0.140, w), (0.075, w)] if sgn > 0 else [(0.075, w), (0.140, w)], 72)
        put("brake_disc", P, F, N)
    P, N, F, _ = lathe([(0.140, -0.052), (0.140, -0.030)], 72)
    put("brake_disc", P, F, N)
    P, N, F, _ = lathe([(0.075, -0.030), (0.074, 0.030), (0.040, 0.034)], 48)
    put("dark", P, F, N)

    # etrierul (sus-spate)
    ang = math.radians(150)
    ca, sa = math.cos(ang), math.sin(ang)
    pos, faces = superellipsoid((0, 0, -0.030), (0.028, 0.052, 0.030), 0.35, 0.35, 10, 20)
    rot = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1]])
    pos = pos @ rot.T + np.array([0.128 * ca, 0.128 * sa, 0])
    put("caliper", pos, faces)

    # butucul si inelul exterior al fetei: suprafete de revolutie, cu pereti spre goluri
    r_hub, r_out, depth = 0.088, 0.184, 0.022
    for prof in ([(r_hub, face_w(r_hub)), (0.060, face_w(0.060) - 0.001), (R_FACE_IN, face_w(R_FACE_IN))],
                 [(r_hub, face_w(r_hub) - depth), (r_hub, face_w(r_hub))],
                 [(R_FACE_OUT, face_w(R_FACE_OUT)), (r_out, face_w(r_out))],
                 [(r_out, face_w(r_out)), (r_out, face_w(r_out) - depth)]):
        P, N, F, _ = lathe(prof, 120)
        put("rim", P, F, N)

    # spitele: 5 perechi in V, fiecare o panglica bombata cu pereti laterali
    rs = np.linspace(r_hub - 0.004, r_out + 0.004, 18)
    across = np.linspace(-1, 1, 7)
    for k in range(5):
        base = math.pi / 2 + 2 * math.pi * k / 5
        for s in (-1, 1):
            top = np.zeros((len(rs), len(across), 3))
            edges = {-1: [], 1: []}
            for i, r in enumerate(rs):
                tt = float(np.clip((r - 0.088) / 0.096, 0, 1))
                center = base + s * (0.150 + tt * 0.080)
                half = (0.0085 + 0.0055 * tt) / r
                for c, f in enumerate(across):
                    th = center + f * half
                    top[i, c] = (r * math.cos(th), r * math.sin(th), face_w(r) + 0.0035 * (1 - f * f))
                for e in (-1, 1):
                    th = center + e * half
                    edges[e].append(((r * math.cos(th), r * math.sin(th), face_w(r)),
                                     (r * math.cos(th), r * math.sin(th), face_w(r) - depth),
                                     (-math.sin(th) * e, math.cos(th) * e, 0.0)))
            F = grid_faces(len(rs), len(across))
            P = top.reshape(-1, 3)
            put("rim", P, _outward_axis(P, F))
            for e in (-1, 1):
                wp = np.array([q for a, b, _ in edges[e] for q in (a, b)])
                wn = np.array([n for _, _, n in edges[e] for _ in (0, 1)])
                WF = grid_faces(len(rs), 2)
                p0, p1, p2 = wp[WF[0, 0]], wp[WF[0, 1]], wp[WF[0, 2]]
                if np.dot(np.cross(p1 - p0, p2 - p0), wn[WF[0, 0]]) < 0:
                    WF = WF[:, ::-1]
                put("rim", wp, WF, wn)

    # prezoane (5 x 110) intre perechile de spite
    for k in range(5):
        a = math.pi / 2 + 2 * math.pi * k / 5 + math.pi / 5
        cx, cy = 0.055 * math.cos(a), 0.055 * math.sin(a)
        hexp = [(0.0095, face_w(0.055) - 0.004), (0.0095, face_w(0.055) + 0.008), (0.0, face_w(0.055) + 0.009)]
        P, N, F, _ = lathe(hexp, 6, phase=math.pi / 6)
        P[:, 0] += cx
        P[:, 1] += cy
        put("chrome", P, F, N)

    # capacul central cu emblema
    cap_w = face_w(R_FACE_IN) + 0.004
    ring = 40
    th = np.linspace(0, 2 * math.pi, ring, endpoint=False)
    pos = [(0, 0, cap_w + 0.004)] + [(0.034 * math.cos(t), 0.034 * math.sin(t), cap_w) for t in th]
    faces = [(0, 1 + i, 1 + (i + 1) % ring) for i in range(ring)]
    uv = [(0.5, 0.5)] + [(0.5 + 0.5 * math.cos(t), 0.5 - 0.5 * math.sin(t)) for t in th]
    nrm = [(0, 0, 1)] + [(0.12 * math.cos(t), 0.12 * math.sin(t), 0.99) for t in th]
    put("cap", pos, _outward_axis(np.array(pos), np.array(faces)), nrm, np.array(uv))
    return parts


def grid_faces(ni, nj):
    """Triunghiurile unei grile ni x nj (fara inchidere)."""
    f = []
    for i in range(ni - 1):
        for j in range(nj - 1):
            a, b, c, d = i * nj + j, i * nj + j + 1, (i + 1) * nj + j + 1, (i + 1) * nj + j
            f += [(a, b, c), (a, c, d)]
    return np.array(f)


def _outward_axis(pos, faces):
    """Fete orientate spre +w (exteriorul rotii)."""
    p0, p1, p2 = pos[faces[:, 0]], pos[faces[:, 1]], pos[faces[:, 2]]
    if np.cross(p1 - p0, p2 - p0)[:, 2].sum() < 0:
        faces = faces[:, ::-1]
    return faces


def add_wheels(scene: Scene):
    parts = wheel_parts()
    for side, mesh in ((1, "roata_dreapta"), (-1, "roata_stanga")):
        for mat, items in parts.items():
            for pos, nrm, faces, uv in items:
                P = pos[:, [0, 1, 2]].copy()
                N = nrm.copy()
                if side < 0:
                    P[:, 2] *= -1
                    N[:, 2] *= -1
                    faces = faces[:, ::-1]
                    if uv is not None and mat == "tire":
                        uv = np.column_stack([1 - uv[:, 0], uv[:, 1]])
                scene.prim(mesh, mat).add(P, N, faces, uv)
    for name, x in (("fata", g.AXLE_F), ("spate", g.AXLE_R)):
        scene.node(f"roata_{name}_dreapta", "roata_dreapta", (x, g.WHEEL_Y, g.WHEEL_Z))
        scene.node(f"roata_{name}_stanga", "roata_stanga", (x, g.WHEEL_Y, -g.WHEEL_Z))


# ----------------------------------------------------------------------------- pasaje de roata
def add_liners(scene: Scene, mesh="caroserie"):
    z_in = 0.565
    for xa in (g.AXLE_F, g.AXLE_R):
        for side in (1, -1):
            y_floor = 0.205
            a0 = math.asin((y_floor - g.WHEEL_Y) / g.ARCH_R)
            th = np.linspace(a0, math.pi - a0, 48)
            r = g.ARCH_R + 0.004
            pos, faces = [], []
            for zi, z in enumerate((z_in, g.HW - 0.004)):
                for t in th:
                    pos.append((xa + r * math.cos(t), g.WHEEL_Y + r * math.sin(t), side * z))
            n = len(th)
            for k in range(n - 1):
                faces += [(k, k + 1, n + k + 1), (k, n + k + 1, n + k)]
            pos = np.array(pos)
            nrm = np.array([(-math.cos(t), -math.sin(t), 0) for t in th] * 2)
            add(scene, mesh, "liner", pos, faces, nrm)
            # peretele interior
            wall = [(xa, max(g.WHEEL_Y, y_floor + 0.05), side * z_in)] + [(xa + r * math.cos(t), g.WHEEL_Y + r * math.sin(t), side * z_in) for t in th]
            wf = [(0, k + 1, k + 2) for k in range(n - 1)]
            wn = np.tile([0, 0, side], (len(wall), 1)).astype(float)
            add(scene, mesh, "liner", wall, wf, wn)


# ----------------------------------------------------------------------------- oglinzi, manere, bare
def add_mirrors(scene: Scene, body: g.Body, mesh="caroserie"):
    for side in (1, -1):
        zb = side_z(body, 0.90, 1.02)
        cx, cy, cz = 0.855, 1.070, side * (zb + 0.098)
        pos, faces = superellipsoid((cx, cy, cz), (0.062, 0.064, 0.094), 0.45, 0.45, 16, 32)
        # spatele carcasei este plat (acolo e oglinda)
        pos[:, 0] = np.maximum(pos[:, 0], cx - 0.030)
        add(scene, mesh, "paint", pos, faces)
        # oglinda
        t = np.linspace(0, 2 * math.pi, 32, endpoint=False)
        gl = [(cx - 0.0315, cy, cz)] + [(cx - 0.0315, cy + 0.052 * np.sign(math.sin(a)) * abs(math.sin(a)) ** 0.6,
                                         cz + 0.080 * np.sign(math.cos(a)) * abs(math.cos(a)) ** 0.6) for a in t]
        gf = np.array([(0, 1 + k, 1 + (k + 1) % 32) for k in range(32)])
        gl = np.array(gl)
        if np.cross(gl[gf[0, 1]] - gl[0], gl[gf[0, 2]] - gl[0])[0] > 0:
            gf = gf[:, ::-1]
        add(scene, mesh, "mirror", gl, gf, np.tile([-1.0, 0, 0], (len(gl), 1)))
        # bratul de prindere, negru
        pos, faces = superellipsoid((0.885, 1.022, side * (zb + 0.030)), (0.045, 0.022, 0.040), 0.4, 0.4, 8, 16)
        add(scene, mesh, "black", pos, faces)


def add_handles(scene: Scene, body: g.Body, mesh="caroserie"):
    for side in (1, -1):
        for x0, x1 in ((0.060, 0.210), (-0.830, -0.680)):
            xc = 0.5 * (x0 + x1)
            z = side_z(body, xc, 0.925)
            pos, faces = superellipsoid((xc, 0.925, side * (z + 0.004)), (0.074, 0.016, 0.014), 0.4, 0.35, 10, 20)
            add(scene, mesh, "paint", pos, faces)


def add_roof_rails(scene: Scene, body: g.Body, mesh="caroserie"):
    z_r = 0.585
    xs = np.linspace(-2.03, 0.17, 140)
    roof = np.array([top_y(body, x, z_r) for x in xs])
    hh = 0.014
    lift = np.full_like(xs, 0.042)
    for end in (xs[0], xs[-1]):
        d = np.abs(xs - end)
        lift = np.minimum(lift, 0.012 + d / 0.16 * 0.030)
    top = roof + lift + hh
    lift += g.HEIGHT - top.max()
    for side in (1, -1):
        path = np.column_stack([xs, roof + lift, np.full_like(xs, side * z_r)])
        pos, faces = sweep(path, rounded_section(0.016, hh, 20, 0.4))
        add(scene, mesh, "rail", pos, faces)
        # picioarele de prindere, negre
        for xe in (xs[2], xs[-3], -0.93):
            pos, faces = superellipsoid((xe, top_y(body, xe, z_r) + 0.010, side * z_r), (0.05, 0.018, 0.021), 0.4, 0.4, 8, 16)
            add(scene, mesh, "plastic", pos, faces)


def add_wipers(scene: Scene, body: g.Body, mesh="caroserie"):
    for (x0, z0), (x1, z1) in (((1.012, -0.62), (0.975, 0.02)), ((1.012, 0.06), (0.985, 0.60))):
        t = np.linspace(0, 1, 24)
        xs, zs = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
        path = np.column_stack([xs, [top_y(body, x, z) + 0.012 for x, z in zip(xs, zs)], zs])
        pos, faces = sweep(path, rounded_section(0.007, 0.006, 8, 0.5))
        add(scene, mesh, "black", pos, faces)
    # stergatorul lunetei
    ys = np.linspace(1.03, 1.30, 20)
    zs = np.linspace(0.0, -0.36, 20)
    path = np.column_stack([[g.X_TAIL + g.rear_shear(y) - 0.010 for y in ys], ys, zs])
    pos, faces = sweep(path, rounded_section(0.006, 0.006, 8, 0.5))
    add(scene, mesh, "black", pos, faces)


def add_exhaust(scene: Scene, mesh="caroserie"):
    x0, x1, y, z = g.X_TAIL + 0.12, g.X_TAIL + 0.035, 0.290, -0.46
    t = np.linspace(0, 2 * math.pi, 24, endpoint=False)
    path = np.array([(x0, y, z), (x1, y, z)])
    pos, faces = sweep(path, np.column_stack([0.030 * np.cos(t), 0.030 * np.sin(t)]))
    add(scene, mesh, "chrome", pos, faces)

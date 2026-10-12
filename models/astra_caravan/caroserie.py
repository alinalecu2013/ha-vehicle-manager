"""Transforma grila caroseriei in primitive pe materiale, cu UV pentru texturile desfasurate."""

from __future__ import annotations

import numpy as np

import geometrie as g
from glb import Scene, smooth_normals

# Zona acoperita de textura laterala (proiectie X-Y), comuna ambelor flancuri.
SIDE_X = (g.X_R0 - 0.02, g.X_F0 + 0.02)
SIDE_Y = (0.10, 1.47)
FRONT_Y = (0.12, 0.98)
REAR_Y = (0.20, 1.46)


def quad_material(body: g.Body, i: int, j: int) -> str | None:
    if body.removed[i, j]:
        return None
    seg = g.quad_seg(j)
    if i < body.i_r0:
        region = "rear"
    elif i < body.i_f0:
        region = "mid"
    else:
        region = "nose"
    if seg == "A":
        return "under"
    if seg in "BC":
        return {"rear": "rear", "mid": "side", "nose": "front"}[region]
    d = g.row_in_d(j)
    if d == 0:
        return "black"
    if region != "mid":
        return "paint"
    xm = 0.5 * (body.x_of(i) + body.x_of(i + 1))
    if g.COWL[0] <= xm <= g.COWL[1]:
        return "plastic"
    if g.WINDSHIELD[0] <= xm < g.COWL[0]:
        return "glass" if d >= 3 and 0.29 < xm < 1.02 else "black"
    return "paint"


def uv_for(body: g.Body, material: str, i: int, j: int):
    x, y, z = body.P[i, j]
    st = body.stations[i]
    if material == "side":
        u = (body.X0[i, j] - SIDE_X[0]) / (SIDE_X[1] - SIDE_X[0])
        v = (SIDE_Y[1] - y) / (SIDE_Y[1] - SIDE_Y[0]) * 0.5 + (0.0 if z >= 0 else 0.5)
        return u, v
    if material == "front":
        s = np.sign(z) * st["arc"] / body.arc_nose
        return 0.5 - 0.5 * s, (FRONT_Y[1] - y) / (FRONT_Y[1] - FRONT_Y[0])
    if material == "rear":
        s = np.sign(z) * st["arc"] / body.arc_rear
        return 0.5 + 0.5 * s, (REAR_Y[1] - y) / (REAR_Y[1] - REAR_Y[0])
    return None


def add_body(scene: Scene, body: g.Body, mesh: str = "caroserie"):
    P = body.P
    ns = P.shape[0]
    idx = np.arange(ns * g.RING).reshape(ns, g.RING)
    nxt = (np.arange(g.RING) + 1) % g.RING

    quads = {}
    for i in range(ns - 1):
        for j in range(g.RING):
            m = quad_material(body, i, j)
            if m is None:
                continue
            quads.setdefault(m, []).append((i, j))

    # normale comune pentru toata grila (fara quad-urile decupate)
    flat = P.reshape(-1, 3)
    faces = []
    for items in quads.values():
        for i, j in items:
            a, b, c, d = idx[i, j], idx[i + 1, j], idx[i + 1, nxt[j]], idx[i, nxt[j]]
            faces += [(a, b, c), (a, c, d)]
    faces = np.array(faces)
    # orientare spre exterior: volum pozitiv
    p0, p1, p2 = flat[faces[:, 0]], flat[faces[:, 1]], flat[faces[:, 2]]
    flip = np.einsum("ij,ij->i", p0, np.cross(p1, p2)).sum() < 0
    normals = smooth_normals(flat, faces[:, ::-1] if flip else faces)

    for material, items in quads.items():
        verts = {}
        out_faces = []
        uvs = []
        for i, j in items:
            zq = P[i, j, 2] + P[i + 1, nxt[j], 2]
            corner = [(i, j), (i + 1, j), (i + 1, nxt[j]), (i, nxt[j])]
            ids = []
            for ci, cj in corner:
                key = (ci, cj, zq >= 0) if material in ("front", "rear", "side") else (ci, cj)
                if key not in verts:
                    verts[key] = len(verts)
                    uv = uv_for(body, material, ci, cj)
                    if uv is not None and material in ("front", "rear", "side"):
                        # pe axa z = 0 alegem flancul quad-ului
                        if abs(P[ci, cj, 2]) < 1e-9:
                            if material in ("front", "rear"):
                                uv = (0.5, uv[1])
                            else:
                                v = (SIDE_Y[1] - P[ci, cj, 1]) / (SIDE_Y[1] - SIDE_Y[0]) * 0.5
                                uv = (uv[0], v + (0.0 if zq >= 0 else 0.5))
                    uvs.append(uv)
                ids.append(verts[key])
            a, b, c, d = ids
            out_faces += [(a, c, b), (a, d, c)] if flip else [(a, b, c), (a, c, d)]
        order = sorted(verts.items(), key=lambda kv: kv[1])
        gi = np.array([idx[k[0], k[1]] for k, _ in order])
        uv_arr = None
        if material in ("front", "rear", "side"):
            uv_arr = np.array(uvs, float)
        scene.prim(mesh, material).add(flat[gi], normals[gi], np.array(out_faces), uv_arr)
    return flip

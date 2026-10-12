"""Genereaza modelul 3D Opel Astra H Caravan (break) la cote reale, cu texturi PBR.

Utilizare:
    python genereaza.py [iesire.glb] [--numar "B 06 OPL"] [--culoare R,G,B] [--mobil]

--mobil: texturi WebP la jumatate de rezolutie (fisier mai mic, de ~4 ori mai putina memorie video).
Cardul Vehicle Manager recoloreaza vopseaua si rescrie numarul la rulare, pe baza metadatelor
"vm" din materiale, deci acelasi fisier merge pentru orice culoare si orice numar.

Dependente: numpy, Pillow. Totul este procedural: nu se folosesc modele sau texturi straine.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import caroserie  # noqa: E402
import detalii  # noqa: E402
import geometrie as g  # noqa: E402
import texturi as t  # noqa: E402
from glb import Scene  # noqa: E402


def materials(paint_srgb):
    paint = t.linear_color(paint_srgb)
    textured = dict(color=(1, 1, 1, 1), metal=1.0, rough=1.0, clearcoat=1.0, clearcoat_rough=0.04)
    return {
        "paint": dict(label="Vopsea Star Silver", color=paint, metal=0.75, rough=0.36,
                      clearcoat=1.0, clearcoat_rough=0.04),
        "side": dict(textured, label="Flancuri", color_tex="side_c", mr_tex="side_m", clearcoat_tex="side_m"),
        "front": dict(textured, label="Fata", color_tex="front_c", mr_tex="front_m", clearcoat_tex="front_m"),
        "rear": dict(textured, label="Spate", color_tex="rear_c", mr_tex="rear_m", clearcoat_tex="rear_m"),
        "glass": dict(label="Parbriz", color=t.linear_color(t.GLASS), metal=0.0, rough=0.04,
                      clearcoat=1.0, clearcoat_rough=0.0),
        "black": dict(label="Ornamente negre", color=t.linear_color(t.BLACK), metal=0.0, rough=0.28),
        "plastic": dict(label="Plastic negru", color=t.linear_color(t.PLASTIC), metal=0.0, rough=0.70),
        "under": dict(label="Podea", color=(0.012, 0.012, 0.013, 1), metal=0.0, rough=0.9),
        "liner": dict(label="Pasaje roti", color=(0.010, 0.010, 0.011, 1), metal=0.0, rough=0.95, double=True),
        "rail": dict(label="Bare plafon aluminiu", color=(0.78, 0.80, 0.82, 1), metal=1.0, rough=0.24),
        "chrome": dict(label="Crom", color=(0.85, 0.86, 0.88, 1), metal=1.0, rough=0.08),
        "mirror": dict(label="Oglinda", color=(0.80, 0.82, 0.85, 1), metal=1.0, rough=0.02),
        "tire": dict(label="Anvelope 205/55 R16", color=(1, 1, 1, 1), metal=0.0, rough=0.88,
                     color_tex="tire_c", normal_tex="tire_n", normal_scale=0.8),
        "rim": dict(label="Jante aliaj 16", color=(0.66, 0.67, 0.69, 1), metal=1.0, rough=0.28,
                    clearcoat=0.6, clearcoat_rough=0.08, double=True),
        "rim_inner": dict(label="Janta interior", color=(0.30, 0.31, 0.32, 1), metal=1.0, rough=0.5),
        "dark": dict(label="Fuzeta", color=(0.02, 0.02, 0.02, 1), metal=0.3, rough=0.7, double=True),
        "brake_disc": dict(label="Disc frana", color=(0.38, 0.38, 0.38, 1), metal=1.0, rough=0.42),
        "caliper": dict(label="Etrier", color=(0.05, 0.05, 0.055, 1), metal=0.4, rough=0.5),
        "cap": dict(label="Capac janta", color=(1, 1, 1, 1), metal=1.0, rough=1.0, color_tex="cap_c",
                    mr_tex="cap_m"),
    }


def plate_uv(center, arc, y_range):
    """Dreptunghiul numarului in coordonate UV (u0, v0, u1, v1) ale texturii desfasurate."""
    a, y = center
    w, h = t.PLATE_SIZE
    span = y_range[1] - y_range[0]
    return [round((a - w / 2 + arc) / (2 * arc), 5), round((y_range[1] - (y + h / 2)) / span, 5),
            round((a + w / 2 + arc) / (2 * arc), 5), round((y_range[1] - (y - h / 2)) / span, 5)]


def card_metadata(scene: Scene, body: g.Body):
    """Metadate citite de card: ce pixeli sunt vopsea, unde e numarul, culoarea lampilor."""
    paint = {"paint_srgb": list(t.PAINT), "paint_mr": list(t.PAINT_MR)}
    m = scene.materials
    m["paint"]["extras"] = {"vm": {"paint": True}}
    m["side"]["extras"] = {"vm": dict(paint)}
    m["front"]["extras"] = {"vm": dict(paint, lamp=[255, 244, 225],
                                       plate=plate_uv(t.FRONT_PLATE, body.arc_nose, caroserie.FRONT_Y))}
    m["rear"]["extras"] = {"vm": dict(paint, lamp=[255, 24, 32],
                                      plate=plate_uv(t.REAR_PLATE, body.arc_rear, caroserie.REAR_Y))}
    m["front"]["emissive_tex"] = "front_e"
    m["rear"]["emissive_tex"] = "rear_e"


def build(out: Path, plate_text: str, paint_srgb, mobile=False):
    t0 = time.time()
    if paint_srgb != t.PAINT:
        t.PAINT = tuple(paint_srgb)
    body = g.Body()
    scene = Scene()
    scene.materials = materials(paint_srgb)
    card_metadata(scene, body)

    caroserie.add_body(scene, body)
    detalii.add_liners(scene)
    detalii.add_mirrors(scene, body)
    detalii.add_handles(scene, body)
    detalii.add_roof_rails(scene, body)
    detalii.add_wipers(scene, body)
    detalii.add_exhaust(scene)
    scene.node("caroserie", "caroserie")
    detalii.add_wheels(scene)

    imgs = {}
    imgs["side_c"], imgs["side_m"] = t.side_textures()
    imgs["front_c"], imgs["front_m"], imgs["front_e"] = t.front_texture(body, plate_text)
    imgs["rear_c"], imgs["rear_m"], imgs["rear_e"] = t.rear_texture(body, plate_text)
    imgs["tire_c"], _, imgs["tire_n"] = t.tire_textures()
    imgs["cap_c"], imgs["cap_m"] = t.cap_texture()
    for key, img in imgs.items():
        exact = key.endswith(("_m", "_n", "_e"))
        if mobile:
            if img.width > 512:
                img = img.resize((img.width // 2, img.height // 2), t.Image.LANCZOS)
            scene.images[key] = t.encode(img, "webp_lossless" if exact else "webp", 86)
        else:
            scene.images[key] = t.encode(img, "png" if exact else "jpeg")

    credit = ("Opel Astra H Caravan, model procedural vehicle_manager (MIT). "
              "Cote: 4515 x 1794 x 1500 mm, ampatament 2703 mm, ecartament 1488 mm.")
    stats = scene.write(out, credit)
    print(f"scris: {out}  ({stats['bytes'] / 1e6:.2f} MB, {stats['triangles']:,} triunghiuri, "
          f"{stats['vertices']:,} varfuri, {time.time() - t0:.1f} s)")
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default="Opel_Astra_H_Caravan.glb")
    ap.add_argument("--numar", default="B 06 OPL", help="textul numarului de inmatriculare")
    ap.add_argument("--culoare", default=",".join(map(str, t.PAINT)), help="culoarea vopselei, sRGB R,G,B")
    ap.add_argument("--mobil", action="store_true", help="texturi WebP la jumatate de rezolutie")
    a = ap.parse_args()
    build(Path(a.out), a.numar, tuple(int(c) for c in a.culoare.split(",")), a.mobil)


if __name__ == "__main__":
    main()

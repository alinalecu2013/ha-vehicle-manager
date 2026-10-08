"""Generator .glb pentru un model stilizat de Opel Astra H Caravan (2007), gri.

Caroseria este un loft de secțiuni transversale superelipsoidale de-a lungul axei X,
cu cote reale: lungime 4515 mm, ampatament 2703 mm, latime 1759 mm, inaltime 1500 mm.
Scrie glTF 2.0 binar fara dependente externe (doar numpy).
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

import numpy as np

# ----------------------------------------------------------------------
# Cote Opel Astra H Caravan (metri)
# ----------------------------------------------------------------------
LENGTH = 4.515
WIDTH = 1.759
HEIGHT = 1.500
WHEELBASE = 2.703
TRACK = 1.488

NOSE_X = 2.250
TAIL_X = -2.265
HALF_WIDTH = WIDTH / 2.0

TIRE_RADIUS = 0.316          # 205/55 R16
TIRE_WIDTH = 0.205
RIM_RADIUS = 0.203           # janta 16"
AXLE_X = WHEELBASE / 2.0
WHEEL_Z = TRACK / 2.0

SHOULDER_Y = 0.80            # inaltimea celui mai lat punct al caroseriei
BELT_Y = 1.035               # linia de centura (baza geamurilor)

SECTION_EXP = 0.42           # 2/n pentru superelipsa: mai mic = mai cubic
TAPER_TOP = 0.235            # plafonul e mai ingust decat centura
TAPER_BOTTOM = 0.260         # pragurile sunt retrase, ca roțile sa iasa din aripi

RING_SEGMENTS = 56
ROOF_HALF_WIDTH = 0.460      # dincolo de aceasta latime incepe geamul lateral
WINDSHIELD_HALF_WIDTH = 0.620  # semi-latimea parbrizului si a lunetei

# Pilonii ramân vopsiți, restul greenhouse-ului devine geam.
PILLARS = ((0.60, 0.76), (-0.16, -0.02), (-1.04, -0.90))

# Profil lateral: (x, y_jos, y_sus, semi-latime)
STATIONS = (
    (NOSE_X, 0.400, 0.840, 0.700),
    (2.215, 0.320, 0.886, 0.792),
    (2.150, 0.288, 0.918, 0.838),
    (2.090, 0.272, 0.946, 0.860),
    (1.900, 0.258, 0.986, 0.873),
    (1.620, 0.250, 1.016, 0.878),
    (AXLE_X, 0.246, 1.040, HALF_WIDTH),
    (1.070, 0.246, 1.070, HALF_WIDTH),
    (0.900, 0.246, 1.110, HALF_WIDTH),
    (0.760, 0.247, 1.170, HALF_WIDTH),
    (0.580, 0.248, 1.330, HALF_WIDTH),
    (0.400, 0.249, 1.445, HALF_WIDTH),
    (0.250, 0.250, 1.492, HALF_WIDTH),
    (0.050, 0.250, 1.500, HALF_WIDTH),
    (-0.020, 0.250, 1.500, HALF_WIDTH),
    (-0.160, 0.251, 1.500, HALF_WIDTH),
    (-0.400, 0.251, 1.500, HALF_WIDTH),
    (-0.900, 0.252, 1.500, HALF_WIDTH),
    (-1.040, 0.253, 1.500, HALF_WIDTH),
    (-AXLE_X, 0.254, 1.500, HALF_WIDTH),
    (-1.700, 0.258, 1.498, 0.878),
    (-1.800, 0.260, 1.495, 0.876),
    (-1.950, 0.264, 1.488, 0.871),
    (-2.120, 0.274, 1.462, 0.862),
    (-2.215, 0.292, 1.420, 0.820),
    (TAIL_X, 0.380, 1.355, 0.700),
)


# ----------------------------------------------------------------------
# Acumulator de geometrie
# ----------------------------------------------------------------------
class Mesh:
    """Colecteaza varfuri si triunghiuri grupate pe material."""

    def __init__(self) -> None:
        self.vertices: list[tuple[float, float, float]] = []
        self.groups: dict[str, list[tuple[int, int, int]]] = {}

    def add_vertices(self, points) -> int:
        base = len(self.vertices)
        self.vertices.extend(tuple(float(c) for c in p) for p in points)
        return base

    def add_triangle(self, material: str, a: int, b: int, c: int) -> None:
        self.groups.setdefault(material, []).append((a, b, c))

    def add_quad(self, material: str, a: int, b: int, c: int, d: int) -> None:
        self.add_triangle(material, a, b, c)
        self.add_triangle(material, a, c, d)

    # -- utilitare -----------------------------------------------------
    def face_center(self, tri) -> np.ndarray:
        pts = np.array([self.vertices[i] for i in tri])
        return pts.mean(axis=0)

    def face_normal(self, tri) -> np.ndarray:
        p0, p1, p2 = (np.array(self.vertices[i]) for i in tri)
        normal = np.cross(p1 - p0, p2 - p0)
        length = np.linalg.norm(normal)
        return normal / length if length > 1e-12 else normal

    def orient_outward(self, triangles: list[tuple[int, int, int]]) -> None:
        """Inverseaza winding-ul unui solid inchis daca volumul iese negativ."""
        volume = 0.0
        for a, b, c in triangles:
            v0, v1, v2 = (np.array(self.vertices[i]) for i in (a, b, c))
            volume += float(np.dot(v0, np.cross(v1, v2))) / 6.0
        if volume < 0:
            for index, (a, b, c) in enumerate(triangles):
                triangles[index] = (a, c, b)


# ----------------------------------------------------------------------
# Caroserie
# ----------------------------------------------------------------------
def section_points(x: float, y_bottom: float, y_top: float, half_width: float):
    """Secțiune transversala superelipsoidala, orientata trigonometric."""
    thetas = np.linspace(0.0, 2.0 * np.pi, RING_SEGMENTS, endpoint=False)
    cos_t, sin_t = np.cos(thetas), np.sin(thetas)

    z_factor = np.sign(cos_t) * np.abs(cos_t) ** SECTION_EXP
    y_factor = np.sign(sin_t) * np.abs(sin_t) ** SECTION_EXP

    up = np.clip(y_factor, 0.0, None)
    down = np.clip(-y_factor, 0.0, None)
    y = SHOULDER_Y + up * (y_top - SHOULDER_Y) - down * (SHOULDER_Y - y_bottom)
    width = half_width * (1.0 - TAPER_TOP * up**1.5 - TAPER_BOTTOM * down**1.5)

    return np.column_stack([np.full_like(y, x), y, width * z_factor])


def in_pillar(x: float) -> bool:
    return any(low <= x <= high for low, high in PILLARS)


def region_for(mid_x: float) -> str:
    """Zona de caroserie careia ii apartine banda dintre doua secțiuni."""
    if mid_x <= -1.950:
        return "rear"
    if 0.240 <= mid_x <= 0.700:
        return "windshield"
    if -1.800 <= mid_x <= 0.660 and not in_pillar(mid_x):
        return "side"
    return "none"


# Randurile 0..CREST formeaza sfertul care urca de la umar la plafon; randul
# CREST este creasta, iar ARC - CREST oglindeste partea cealalta.
CREST = RING_SEGMENTS // 4
ARC = RING_SEGMENTS // 2


def latitude(row: int) -> int:
    """Distanța unui rand fața de umar, identica pe ambele flancuri."""
    return row if row <= CREST else ARC - row


def row_at_y(section, value: float) -> int:
    """Primul rand care atinge inaltimea data, urcand dinspre umar."""
    for row in range(CREST + 1):
        if float(section[row][1]) >= value:
            return row
    return CREST + 1


def row_at_depth(section, value: float) -> int:
    """Primul rand al carui |z| coboara sub valoarea data."""
    for row in range(CREST + 1):
        if abs(float(section[row][2])) <= value:
            return row
    return CREST + 1


def build_body(mesh: Mesh) -> None:
    sections = [section_points(*station) for station in STATIONS]
    bases = [mesh.add_vertices(section) for section in sections]

    shell: list[tuple[int, int, int]] = []
    materials: list[str] = []

    for index in range(len(sections) - 1):
        section_a, section_b = sections[index], sections[index + 1]
        base_a, base_b = bases[index], bases[index + 1]
        mid_x = (STATIONS[index][0] + STATIONS[index + 1][0]) / 2.0
        region = region_for(mid_x)

        def threshold(fn, value):
            """Pragul comun celor doua secțiuni ale benzii."""
            return max(fn(section_a, value), fn(section_b, value))

        belt = threshold(row_at_y, BELT_Y + 0.020)
        roof = threshold(row_at_depth, ROOF_HALF_WIDTH)
        pane = threshold(row_at_depth, WINDSHIELD_HALF_WIDTH)
        lamp_low = threshold(row_at_y, 0.690)
        lamp_high = threshold(row_at_y, 0.900)
        grille_low = threshold(row_at_y, 0.560)
        intake_low = threshold(row_at_y, 0.330)
        intake_high = threshold(row_at_y, 0.500)
        grille_depth = threshold(row_at_depth, 0.520)
        intake_depth = threshold(row_at_depth, 0.640)
        tail_low = threshold(row_at_y, 0.980)
        tail_high = threshold(row_at_y, 1.400)
        tail_inner = threshold(row_at_depth, 0.520)
        tail_outer = threshold(row_at_depth, 0.800)
        lamp_inner = threshold(row_at_depth, 0.260)
        lamp_outer = threshold(row_at_depth, 0.680)

        for j in range(RING_SEGMENTS):
            k = (j + 1) % RING_SEGMENTS
            material = "paint"

            if j < ARC:
                lo = min(latitude(j), latitude(k))
                hi = max(latitude(j), latitude(k))
                above_belt = lo >= belt

                if region == "windshield" and above_belt and lo >= pane:
                    material = "glass"
                elif region == "side" and above_belt and hi < roof:
                    material = "glass"
                elif region == "rear" and above_belt and lo >= roof:
                    material = "glass"
                elif (
                    mid_x >= 2.120
                    and lamp_low <= lo
                    and hi < lamp_high
                    and lo >= lamp_outer
                    and hi < lamp_inner
                ):
                    material = "lamp_front"
                elif mid_x >= 2.120 and grille_low <= lo < lamp_low and lo >= grille_depth:
                    material = "trim"
                elif mid_x >= 2.150 and intake_low <= lo < intake_high and lo >= intake_depth:
                    material = "trim"
                elif (
                    mid_x <= -2.100
                    and tail_low <= lo < tail_high
                    and lo >= tail_outer
                    and hi < tail_inner
                ):
                    material = "lamp_rear"

            a, b = base_a + j, base_a + k
            c, d = base_b + k, base_b + j
            shell.extend([(a, b, c), (a, c, d)])
            materials.extend([material, material])

    # Capace plate la fața si la haion.
    for base, section in ((bases[0], sections[0]), (bases[-1], sections[-1])):
        center_index = mesh.add_vertices([section.mean(axis=0)])
        for j in range(RING_SEGMENTS):
            k = (j + 1) % RING_SEGMENTS
            shell.append((center_index, base + j, base + k))
            materials.append("paint")

    mesh.orient_outward(shell)
    for tri, material in zip(shell, materials):
        mesh.add_triangle(material, *tri)


# ----------------------------------------------------------------------
# Roți
# ----------------------------------------------------------------------
def build_wheel(mesh: Mesh, x: float, z: float) -> None:
    segments = 32
    thetas = np.linspace(0.0, 2.0 * np.pi, segments, endpoint=False)
    half = TIRE_WIDTH / 2.0
    inner_z, outer_z = z - np.sign(z) * half, z + np.sign(z) * half

    cos_t, sin_t = np.cos(thetas), np.sin(thetas)
    tread_in = np.column_stack(
        [x + TIRE_RADIUS * cos_t, TIRE_RADIUS + TIRE_RADIUS * sin_t, np.full(segments, inner_z)]
    )
    tread_out = np.column_stack(
        [x + TIRE_RADIUS * cos_t, TIRE_RADIUS + TIRE_RADIUS * sin_t, np.full(segments, outer_z)]
    )
    rim_in = np.column_stack(
        [x + RIM_RADIUS * cos_t, TIRE_RADIUS + RIM_RADIUS * sin_t, np.full(segments, inner_z)]
    )
    rim_out = np.column_stack(
        [x + RIM_RADIUS * cos_t, TIRE_RADIUS + RIM_RADIUS * sin_t, np.full(segments, outer_z)]
    )

    base_ti = mesh.add_vertices(tread_in)
    base_to = mesh.add_vertices(tread_out)
    base_ri = mesh.add_vertices(rim_in)
    base_ro = mesh.add_vertices(rim_out)

    tire: list[tuple[int, int, int]] = []
    for j in range(segments):
        k = (j + 1) % segments
        # banda de rulare
        tire.extend(
            [
                (base_ti + j, base_ti + k, base_to + k),
                (base_ti + j, base_to + k, base_to + j),
            ]
        )
        # flancuri, pana la janta
        tire.extend(
            [
                (base_ti + j, base_ri + j, base_ri + k),
                (base_ti + j, base_ri + k, base_ti + k),
                (base_to + j, base_ro + k, base_ro + j),
                (base_to + j, base_to + k, base_ro + k),
            ]
        )
    mesh.orient_outward(tire)
    for tri in tire:
        mesh.add_triangle("tire", *tri)

    # Discul jantei, retras ușor spre interior.
    disc_z = z + np.sign(z) * (half - 0.018)
    disc = np.column_stack(
        [x + RIM_RADIUS * cos_t, TIRE_RADIUS + RIM_RADIUS * sin_t, np.full(segments, disc_z)]
    )
    base_disc = mesh.add_vertices(disc)
    hub = mesh.add_vertices([[x, TIRE_RADIUS, disc_z]])
    outward = 1 if z > 0 else -1
    for j in range(segments):
        k = (j + 1) % segments
        if outward > 0:
            mesh.add_triangle("rim", hub, base_disc + j, base_disc + k)
        else:
            mesh.add_triangle("rim", hub, base_disc + k, base_disc + j)


# ----------------------------------------------------------------------
# Detalii: lampi, grila, oglinzi, bare de plafon
# ----------------------------------------------------------------------
def build_box(mesh: Mesh, material: str, center, size) -> None:
    """Cutie cu varfuri duplicate per fața, ca sa pastreze muchiile vii."""
    cx, cy, cz = center
    hx, hy, hz = (s / 2.0 for s in size)

    corners = {
        "x+": [(cx + hx, cy - hy, cz - hz), (cx + hx, cy - hy, cz + hz),
               (cx + hx, cy + hy, cz + hz), (cx + hx, cy + hy, cz - hz)],
        "x-": [(cx - hx, cy - hy, cz + hz), (cx - hx, cy - hy, cz - hz),
               (cx - hx, cy + hy, cz - hz), (cx - hx, cy + hy, cz + hz)],
        "y+": [(cx - hx, cy + hy, cz - hz), (cx + hx, cy + hy, cz - hz),
               (cx + hx, cy + hy, cz + hz), (cx - hx, cy + hy, cz + hz)],
        "y-": [(cx - hx, cy - hy, cz + hz), (cx + hx, cy - hy, cz + hz),
               (cx + hx, cy - hy, cz - hz), (cx - hx, cy - hy, cz - hz)],
        "z+": [(cx - hx, cy - hy, cz + hz), (cx - hx, cy + hy, cz + hz),
               (cx + hx, cy + hy, cz + hz), (cx + hx, cy - hy, cz + hz)],
        "z-": [(cx + hx, cy - hy, cz - hz), (cx + hx, cy + hy, cz - hz),
               (cx - hx, cy + hy, cz - hz), (cx - hx, cy - hy, cz - hz)],
    }
    faces: list[tuple[int, int, int]] = []
    for quad in corners.values():
        base = mesh.add_vertices(quad)
        faces.extend([(base, base + 1, base + 2), (base, base + 2, base + 3)])
    mesh.orient_outward(faces)
    for tri in faces:
        mesh.add_triangle(material, *tri)


def build_details(mesh: Mesh) -> None:
    # Oglinzi, prinse de caroserie la baza stalpului A
    for z in (0.912, -0.912):
        build_box(mesh, "trim", (0.605, 1.058, z), (0.150, 0.105, 0.195))
    # Bare longitudinale de plafon
    for z in (0.520, -0.520):
        build_box(mesh, "trim", (-0.925, 1.472, z), (1.950, 0.055, 0.060))
    # Luneta, aplicata pe fața plana a haionului
    build_box(mesh, "glass", (TAIL_X - 0.004, 1.215, 0.0), (0.014, 0.260, 0.880))
    # Evacuare
    build_box(mesh, "trim", (-2.210, 0.330, 0.50), (0.090, 0.065, 0.085))


# ----------------------------------------------------------------------
# Scriere glTF 2.0 binar
# ----------------------------------------------------------------------
MATERIALS = {
    "paint": {
        "name": "Caroserie gri",
        "pbrMetallicRoughness": {
            "baseColorFactor": [0.557, 0.580, 0.604, 1.0],
            "metallicFactor": 0.55,
            "roughnessFactor": 0.32,
        },
    },
    "glass": {
        "name": "Geamuri",
        "pbrMetallicRoughness": {
            "baseColorFactor": [0.039, 0.059, 0.082, 1.0],
            "metallicFactor": 0.10,
            "roughnessFactor": 0.06,
        },
    },
    "tire": {
        "name": "Anvelope",
        "pbrMetallicRoughness": {
            "baseColorFactor": [0.082, 0.094, 0.110, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.92,
        },
    },
    "rim": {
        "name": "Jante",
        "pbrMetallicRoughness": {
            "baseColorFactor": [0.772, 0.800, 0.827, 1.0],
            "metallicFactor": 1.0,
            "roughnessFactor": 0.22,
        },
    },
    "lamp_front": {
        "name": "Faruri",
        "pbrMetallicRoughness": {
            "baseColorFactor": [0.910, 0.949, 0.973, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.10,
        },
        "emissiveFactor": [0.30, 0.34, 0.38],
    },
    "lamp_rear": {
        "name": "Stopuri",
        "pbrMetallicRoughness": {
            "baseColorFactor": [0.549, 0.059, 0.094, 1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.22,
        },
        "emissiveFactor": [0.42, 0.04, 0.06],
    },
    "trim": {
        "name": "Ornamente",
        "pbrMetallicRoughness": {
            "baseColorFactor": [0.106, 0.122, 0.141, 1.0],
            "metallicFactor": 0.35,
            "roughnessFactor": 0.48,
        },
    },
}

MATERIAL_ORDER = ("paint", "glass", "tire", "rim", "lamp_front", "lamp_rear", "trim")


def smooth_normals(vertices: np.ndarray, all_faces: np.ndarray) -> np.ndarray:
    """Normale per varf, acumulate din toate fețele care il folosesc."""
    normals = np.zeros_like(vertices)
    p0 = vertices[all_faces[:, 0]]
    p1 = vertices[all_faces[:, 1]]
    p2 = vertices[all_faces[:, 2]]
    face_normals = np.cross(p1 - p0, p2 - p0)
    for column in range(3):
        np.add.at(normals, all_faces[:, column], face_normals)
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    lengths[lengths < 1e-12] = 1.0
    return (normals / lengths).astype(np.float32)


def write_glb(path: Path, mesh: Mesh, name: str) -> dict:
    vertices = np.array(mesh.vertices, dtype=np.float32)
    present = [m for m in MATERIAL_ORDER if mesh.groups.get(m)]
    all_faces = np.concatenate(
        [np.array(mesh.groups[m], dtype=np.uint32) for m in present]
    )
    normals = smooth_normals(vertices, all_faces)

    blobs: list[bytes] = []
    buffer_views: list[dict] = []
    accessors: list[dict] = []
    offset = 0

    def append(data: bytes, target: int) -> int:
        nonlocal offset
        padding = (-len(data)) % 4
        blobs.append(data + b"\x00" * padding)
        buffer_views.append(
            {"buffer": 0, "byteOffset": offset, "byteLength": len(data), "target": target}
        )
        offset += len(data) + padding
        return len(buffer_views) - 1

    position_view = append(vertices.tobytes(), 34962)
    accessors.append(
        {
            "bufferView": position_view,
            "componentType": 5126,
            "count": int(len(vertices)),
            "type": "VEC3",
            "min": [float(v) for v in vertices.min(axis=0)],
            "max": [float(v) for v in vertices.max(axis=0)],
        }
    )
    normal_view = append(normals.tobytes(), 34962)
    accessors.append(
        {
            "bufferView": normal_view,
            "componentType": 5126,
            "count": int(len(normals)),
            "type": "VEC3",
        }
    )

    primitives = []
    for material_name in present:
        indices = np.array(mesh.groups[material_name], dtype=np.uint32).ravel()
        view = append(indices.tobytes(), 34963)
        accessors.append(
            {
                "bufferView": view,
                "componentType": 5125,
                "count": int(len(indices)),
                "type": "SCALAR",
            }
        )
        primitives.append(
            {
                "attributes": {"POSITION": 0, "NORMAL": 1},
                "indices": len(accessors) - 1,
                "material": present.index(material_name),
                "mode": 4,
            }
        )

    binary = b"".join(blobs)
    gltf = {
        "asset": {
            "version": "2.0",
            "generator": "vehicle_manager procedural car generator",
        },
        "scene": 0,
        "scenes": [{"nodes": [0], "name": name}],
        "nodes": [{"mesh": 0, "name": name}],
        "meshes": [{"name": name, "primitives": primitives}],
        "materials": [
            dict(MATERIALS[m], doubleSided=(m in ("glass", "rim"))) for m in present
        ],
        "accessors": accessors,
        "bufferViews": buffer_views,
        "buffers": [{"byteLength": len(binary)}],
    }

    json_bytes = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    json_bytes += b" " * ((-len(json_bytes)) % 4)

    total = 12 + 8 + len(json_bytes) + 8 + len(binary)
    with path.open("wb") as handle:
        handle.write(struct.pack("<III", 0x46546C67, 2, total))
        handle.write(struct.pack("<II", len(json_bytes), 0x4E4F534A))
        handle.write(json_bytes)
        handle.write(struct.pack("<II", len(binary), 0x004E4942))
        handle.write(binary)

    return {
        "vertices": len(vertices),
        "triangles": len(all_faces),
        "primitives": {m: len(mesh.groups[m]) for m in present},
        "size": vertices.max(axis=0) - vertices.min(axis=0),
        "bytes": total,
    }


def main() -> None:
    mesh = Mesh()
    build_body(mesh)
    for x in (AXLE_X, -AXLE_X):
        for z in (WHEEL_Z, -WHEEL_Z):
            build_wheel(mesh, x, z)
    build_details(mesh)

    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    stats = write_glb(out, mesh, "Opel Astra H Caravan")

    print(f"scris: {out}")
    print(f"  varfuri      : {stats['vertices']:,}")
    print(f"  triunghiuri  : {stats['triangles']:,}")
    print(f"  dimensiune   : {stats['bytes']:,} B")
    size = stats["size"]
    print(f"  gabarit L/H/W: {size[0]:.3f} x {size[1]:.3f} x {size[2]:.3f} m")
    print(f"  asteptat     : {LENGTH:.3f} x {HEIGHT:.3f} x {WIDTH:.3f} m")
    for material, count in stats["primitives"].items():
        print(f"  {material:<11}: {count:,} triunghiuri")


if __name__ == "__main__":
    main()

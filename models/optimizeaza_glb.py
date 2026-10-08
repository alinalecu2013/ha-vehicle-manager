"""Reduce un .glb pentru afisare intr-un card Lovelace.

Pastreaza exteriorul si arunca ce nu se vede: geometria de interior, atributele
TANGENT (three.js le deduce din derivate), animatiile si tot ce ramane
nereferentiat. Reindexeaza pe 16 biti unde se poate.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

import numpy as np

COMPONENT = {
    5120: ("<i1", 1),
    5121: ("<u1", 1),
    5122: ("<i2", 2),
    5123: ("<u2", 2),
    5125: ("<u4", 4),
    5126: ("<f4", 4),
}
TYPE_COUNT = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}

# Materiale care imbraca exclusiv interiorul sau mecanica ascunsa.
DROP_MATERIALS = {
    "Leather_seat",
    "astrah_ledere",
    "astrah_leatherseat",
    "astrah_tepih",
    "astrah_seatfabric",
    "astrah_sitz",
    "astrah_odometar",
    "astrah_essentia_screen",
    "vivace_mechanical",
    "vivace_engine",
    "Pedal",
}

DROP_ATTRIBUTES = {"TANGENT", "TEXCOORD_1", "COLOR_0", "JOINTS_0", "WEIGHTS_0"}

# Orice ajunge mult peste plafonul masinii este rig de scena, nu caroserie.
ROOF_CUTOFF = 1.70


# ----------------------------------------------------------------------
def load_glb(path: Path):
    data = path.read_bytes()
    magic, version, _total = struct.unpack_from("<III", data, 0)
    if magic != 0x46546C67 or version != 2:
        raise SystemExit("fisierul nu este un GLB v2 valid")

    offset = 12
    gltf, binary = None, b""
    while offset < len(data):
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        payload = data[offset + 8 : offset + 8 + chunk_len]
        if chunk_type == 0x4E4F534A:
            gltf = json.loads(payload.decode("utf-8"))
        elif chunk_type == 0x004E4942:
            binary = payload
        offset += 8 + chunk_len + ((-chunk_len) % 4)
    return gltf, binary


def read_accessor(gltf, binary, index) -> np.ndarray:
    """Citeste un accesor, despachetand si datele intercalate (byteStride)."""
    accessor = gltf["accessors"][index]
    if "sparse" in accessor:
        raise SystemExit("accesori sparse nesuportati")

    dtype, size = COMPONENT[accessor["componentType"]]
    components = TYPE_COUNT[accessor["type"]]
    count = accessor["count"]

    if "bufferView" not in accessor:
        return np.zeros((count, components), dtype=np.dtype(dtype))

    view = gltf["bufferViews"][accessor["bufferView"]]
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    stride = view.get("byteStride") or size * components

    if stride == size * components:
        values = np.frombuffer(binary, dtype=dtype, count=count * components, offset=start)
        return values.reshape(count, components)

    raw = np.frombuffer(binary, dtype=np.uint8, count=stride * count, offset=start)
    raw = raw.reshape(count, stride)[:, : size * components]
    return np.ascontiguousarray(raw).view(dtype).reshape(count, components)


def node_matrix(node) -> np.ndarray:
    """Matricea locala a unui nod, din `matrix` sau din TRS."""
    if "matrix" in node:
        return np.array(node["matrix"], dtype=np.float64).reshape(4, 4).T
    matrix = np.eye(4)
    if "scale" in node:
        matrix[:3, :3] = np.diag(node["scale"])
    if "rotation" in node:
        x, y, z, w = node["rotation"]
        matrix[:3, :3] = np.array([
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]) @ matrix[:3, :3]
    if "translation" in node:
        matrix[:3, 3] = node["translation"]
    return matrix


def nodes_above_roof(gltf) -> set[int]:
    """Noduri al caror gabarit urca peste plafon: piloni, lampi de studio, rig."""
    nodes = gltf.get("nodes", [])
    scene = gltf["scenes"][gltf.get("scene", 0)]
    flagged: set[int] = set()

    stack = [(root, np.eye(4)) for root in scene.get("nodes", [])]
    while stack:
        index, parent = stack.pop()
        node = nodes[index]
        world = parent @ node_matrix(node)
        for child in node.get("children", []):
            stack.append((child, world))
        if "mesh" not in node:
            continue

        top = -1e9
        for prim in gltf["meshes"][node["mesh"]]["primitives"]:
            accessor = gltf["accessors"][prim["attributes"]["POSITION"]]
            if "min" not in accessor:
                continue
            lo, hi = accessor["min"], accessor["max"]
            corners = np.array([[x, y, z, 1.0]
                                for x in (lo[0], hi[0])
                                for y in (lo[1], hi[1])
                                for z in (lo[2], hi[2])])
            top = max(top, float((corners @ world.T)[:, 1].max()))
        if top > ROOF_CUTOFF:
            flagged.add(index)
    return flagged


# ----------------------------------------------------------------------
class Builder:
    """Construieste buffer-ul nou si tine evidenta accesorilor rescrisi."""

    def __init__(self) -> None:
        self.blobs: list[bytes] = []
        self.offset = 0
        self.views: list[dict] = []
        self.accessors: list[dict] = []

    def add_view(self, data: bytes, target: int | None = None, stride: int | None = None) -> int:
        padding = (-len(data)) % 4
        self.blobs.append(data + b"\x00" * padding)
        view = {"buffer": 0, "byteOffset": self.offset, "byteLength": len(data)}
        if target is not None:
            view["target"] = target
        if stride is not None:
            view["byteStride"] = stride
        self.views.append(view)
        self.offset += len(data) + padding
        return len(self.views) - 1

    def add_accessor(self, array: np.ndarray, kind: str, component: int, target: int) -> int:
        view = self.add_view(array.tobytes(), target)
        accessor = {
            "bufferView": view,
            "componentType": component,
            "count": int(array.shape[0]),
            "type": kind,
        }
        if kind == "VEC3" and component == 5126:
            accessor["min"] = [float(v) for v in array.min(axis=0)]
            accessor["max"] = [float(v) for v in array.max(axis=0)]
        self.accessors.append(accessor)
        return len(self.accessors) - 1

    def data(self) -> bytes:
        return b"".join(self.blobs)


# ----------------------------------------------------------------------
def slim(source: Path, target: Path, drop_normal_maps: bool) -> dict:
    gltf, binary = load_glb(source)
    materials = gltf.get("materials", [])

    dropped_materials = {
        i for i, m in enumerate(materials) if m.get("name") in DROP_MATERIALS
    }

    stats = {
        "tris_in": 0,
        "tris_out": 0,
        "tris_dropped": 0,
        "prims_dropped": 0,
        "images_in": len(gltf.get("images", [])),
    }

    dropped_nodes = nodes_above_roof(gltf)
    live_meshes = {
        node["mesh"]
        for i, node in enumerate(gltf.get("nodes", []))
        if "mesh" in node and i not in dropped_nodes
    }

    # --- ce primitive raman ---
    kept: dict[int, list[dict]] = {}
    for mesh_index, mesh in enumerate(gltf["meshes"]):
        survivors = []
        if mesh_index not in live_meshes:
            stats["tris_dropped"] += sum(
                gltf["accessors"][p["indices"]]["count"] // 3
                for p in mesh["primitives"]
                if "indices" in p
            )
            stats["tris_in"] += stats["tris_dropped"] * 0
            continue
        for prim in mesh["primitives"]:
            count = (
                gltf["accessors"][prim["indices"]]["count"] // 3
                if "indices" in prim
                else 0
            )
            stats["tris_in"] += count
            if prim.get("material") in dropped_materials:
                stats["tris_dropped"] += count
                stats["prims_dropped"] += 1
                continue
            survivors.append(prim)
            stats["tris_out"] += count
        if survivors:
            kept[mesh_index] = survivors

    used_materials = sorted(
        {p.get("material") for prims in kept.values() for p in prims if p.get("material") is not None}
    )
    material_map = {old: new for new, old in enumerate(used_materials)}

    # --- rescrie geometria ---
    builder = Builder()
    accessor_cache: dict[tuple, int] = {}

    def copy_attribute(index: int) -> int:
        key = ("attr", index)
        if key in accessor_cache:
            return accessor_cache[key]
        accessor = gltf["accessors"][index]
        array = np.ascontiguousarray(read_accessor(gltf, binary, index))
        new_index = builder.add_accessor(
            array, accessor["type"], accessor["componentType"], 34962
        )
        if accessor.get("normalized"):
            builder.accessors[new_index]["normalized"] = True
        accessor_cache[key] = new_index
        return new_index

    def copy_indices(index: int) -> int:
        key = ("idx", index)
        if key in accessor_cache:
            return accessor_cache[key]
        array = read_accessor(gltf, binary, index).reshape(-1)
        component = 5125
        if array.size and int(array.max()) < 65536:
            array = array.astype(np.uint16)
            component = 5123
        else:
            array = array.astype(np.uint32)
        view = builder.add_view(np.ascontiguousarray(array).tobytes(), 34963)
        builder.accessors.append(
            {
                "bufferView": view,
                "componentType": component,
                "count": int(array.size),
                "type": "SCALAR",
            }
        )
        accessor_cache[key] = len(builder.accessors) - 1
        return accessor_cache[key]

    new_meshes = []
    mesh_map = {}
    for mesh_index, prims in kept.items():
        primitives = []
        for prim in prims:
            attributes = {
                name: copy_attribute(acc)
                for name, acc in prim["attributes"].items()
                if name not in DROP_ATTRIBUTES
            }
            entry = {"attributes": attributes, "mode": prim.get("mode", 4)}
            if "indices" in prim:
                entry["indices"] = copy_indices(prim["indices"])
            if prim.get("material") is not None:
                entry["material"] = material_map[prim["material"]]
            primitives.append(entry)
        mesh_map[mesh_index] = len(new_meshes)
        new_meshes.append(
            {"primitives": primitives, **({"name": gltf["meshes"][mesh_index]["name"]} if "name" in gltf["meshes"][mesh_index] else {})}
        )

    # --- materiale, texturi, imagini ---
    textures = gltf.get("textures", [])
    images = gltf.get("images", [])

    new_materials = []
    used_textures: dict[int, int] = {}

    def remap_texture(ref):
        if ref is None or "index" not in ref:
            return None
        old = ref["index"]
        if old not in used_textures:
            used_textures[old] = len(used_textures)
        clone = dict(ref)
        clone["index"] = used_textures[old]
        return clone

    for old in used_materials:
        material = json.loads(json.dumps(materials[old]))
        pbr = material.get("pbrMetallicRoughness", {})
        for slot in ("baseColorTexture", "metallicRoughnessTexture"):
            if slot in pbr:
                pbr[slot] = remap_texture(pbr[slot])
        for slot in ("emissiveTexture", "occlusionTexture", "normalTexture"):
            if slot in material:
                if slot == "normalTexture" and drop_normal_maps:
                    material.pop(slot)
                else:
                    material[slot] = remap_texture(material[slot])
        extensions = material.get("extensions", {})
        for ext in extensions.values():
            if isinstance(ext, dict):
                for slot, value in list(ext.items()):
                    if isinstance(value, dict) and "index" in value:
                        ext[slot] = remap_texture(value)
        new_materials.append(material)

    used_images: dict[int, int] = {}
    new_textures = [None] * len(used_textures)
    for old, new in used_textures.items():
        texture = dict(textures[old])
        image_index = texture.get("source")
        if image_index is not None:
            if image_index not in used_images:
                used_images[image_index] = len(used_images)
            texture["source"] = used_images[image_index]
        new_textures[new] = texture

    new_images = [None] * len(used_images)
    for old, new in used_images.items():
        image = dict(images[old])
        if "bufferView" in image:
            view = gltf["bufferViews"][image["bufferView"]]
            start = view.get("byteOffset", 0)
            payload = binary[start : start + view["byteLength"]]
            image["bufferView"] = builder.add_view(payload)
        new_images[new] = image

    # --- noduri: pastram ierarhia, doar dezlegam mesh-urile eliminate ---
    new_nodes = []
    for index, node in enumerate(gltf.get("nodes", [])):
        clone = dict(node)
        if "mesh" in clone:
            if clone["mesh"] in mesh_map and index not in dropped_nodes:
                clone["mesh"] = mesh_map[clone["mesh"]]
            else:
                clone.pop("mesh")
        clone.pop("skin", None)
        new_nodes.append(clone)

    binary_out = builder.data()
    out = {
        "asset": {
            "version": "2.0",
            "generator": "vehicle_manager glb slimmer",
            "copyright": gltf.get("asset", {}).get("copyright", ""),
        },
        "scene": gltf.get("scene", 0),
        "scenes": gltf.get("scenes", [{"nodes": [0]}]),
        "nodes": new_nodes,
        "meshes": new_meshes,
        "materials": new_materials,
        "accessors": builder.accessors,
        "bufferViews": builder.views,
        "buffers": [{"byteLength": len(binary_out)}],
    }
    if new_textures:
        out["textures"] = new_textures
    if new_images:
        out["images"] = new_images
    if gltf.get("samplers"):
        out["samplers"] = gltf["samplers"]
    used_ext = sorted(
        {e for m in new_materials for e in m.get("extensions", {})}
    )
    if used_ext:
        out["extensionsUsed"] = used_ext

    json_bytes = json.dumps(out, separators=(",", ":")).encode("utf-8")
    json_bytes += b" " * ((-len(json_bytes)) % 4)
    total = 12 + 8 + len(json_bytes) + 8 + len(binary_out)

    with target.open("wb") as handle:
        handle.write(struct.pack("<III", 0x46546C67, 2, total))
        handle.write(struct.pack("<II", len(json_bytes), 0x4E4F534A))
        handle.write(json_bytes)
        handle.write(struct.pack("<II", len(binary_out), 0x004E4942))
        handle.write(binary_out)

    stats.update(
        {
            "size_in": source.stat().st_size,
            "size_out": total,
            "materials": len(new_materials),
            "images_out": len(new_images),
            "meshes_out": len(new_meshes),
            "nodes_dropped": len(dropped_nodes),
        }
    )
    return stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("target")
    parser.add_argument("--drop-normal-maps", action="store_true")
    args = parser.parse_args()

    stats = slim(Path(args.source), Path(args.target), args.drop_normal_maps)

    print(f"  triunghiuri : {stats['tris_in']:,} -> {stats['tris_out']:,} "
          f"(eliminate {stats['tris_dropped']:,})")
    print(f"  mesh-uri    : {stats['meshes_out']:,}  materiale: {stats['materials']}")
    print(f"  imagini     : {stats['images_in']} -> {stats['images_out']}")
    print(f"  marime      : {stats['size_in']/1048576:.1f} MB -> "
          f"{stats['size_out']/1048576:.1f} MB "
          f"({100 * stats['size_out'] / stats['size_in']:.0f}%)")


if __name__ == "__main__":
    main()

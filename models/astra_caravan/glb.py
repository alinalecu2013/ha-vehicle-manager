"""Scriere glTF 2.0 binar (.glb) cu materiale PBR, texturi incorporate si clearcoat."""

from __future__ import annotations

import json
import struct
from pathlib import Path

import numpy as np


def smooth_normals(pos: np.ndarray, faces: np.ndarray) -> np.ndarray:
    n = np.zeros_like(pos)
    p0, p1, p2 = pos[faces[:, 0]], pos[faces[:, 1]], pos[faces[:, 2]]
    fn = np.cross(p1 - p0, p2 - p0)
    for c in range(3):
        np.add.at(n, faces[:, c], fn)
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    ln[ln < 1e-15] = 1.0
    return n / ln


class Primitive:
    """Triunghiuri ale unui singur material: pozitii, normale, UV optional."""

    def __init__(self, material: str):
        self.material = material
        self.pos, self.nrm, self.uv, self.idx = [], [], [], []
        self.count = 0

    def add(self, pos, nrm, faces, uv=None):
        pos = np.asarray(pos, np.float64)
        self.pos.append(pos)
        self.nrm.append(np.asarray(nrm, np.float64))
        self.uv.append(None if uv is None else np.asarray(uv, np.float64))
        self.idx.append(np.asarray(faces, np.int64) + self.count)
        self.count += len(pos)

    def arrays(self):
        pos = np.concatenate(self.pos)
        nrm = np.concatenate(self.nrm)
        idx = np.concatenate(self.idx)
        has_uv = any(u is not None for u in self.uv)
        uv = None
        if has_uv:
            uv = np.concatenate([u if u is not None else np.zeros((len(p), 2))
                                 for u, p in zip(self.uv, self.pos)])
        return pos, nrm, uv, idx


class Scene:
    """Mesh-uri cu primitive per material, noduri, imagini si materiale."""

    def __init__(self):
        self.meshes: dict[str, dict[str, Primitive]] = {}
        self.nodes: list[dict] = []
        self.materials: dict[str, dict] = {}
        self.images: dict[str, tuple[bytes, str]] = {}
        self.webp = False

    def prim(self, mesh: str, material: str) -> Primitive:
        prims = self.meshes.setdefault(mesh, {})
        if material not in prims:
            prims[material] = Primitive(material)
        return prims[material]

    def node(self, name, mesh, translation=(0, 0, 0)):
        self.nodes.append({"name": name, "mesh": mesh, "translation": [float(v) for v in translation]})

    # ------------------------------------------------------------------ scriere
    def write(self, path: Path, credit: str = "") -> dict:
        blobs, views, accessors = [], [], []
        offset = 0

        def view(data: bytes, target=None):
            nonlocal offset
            pad = (-len(data)) % 4
            blobs.append(data + b"\x00" * pad)
            v = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
            if target:
                v["target"] = target
            views.append(v)
            offset += len(data) + pad
            return len(views) - 1

        def accessor(arr, kind, comp=5126, minmax=False, target=34962):
            a = {"bufferView": view(arr.tobytes(), target), "componentType": comp,
                 "count": int(len(arr)), "type": kind}
            if minmax:
                a["min"] = [float(v) for v in arr.min(axis=0)]
                a["max"] = [float(v) for v in arr.max(axis=0)]
            accessors.append(a)
            return len(accessors) - 1

        # materiale folosite efectiv
        used = []
        for prims in self.meshes.values():
            for name in prims:
                if name not in used:
                    used.append(name)

        image_keys = []
        textures = []

        def texture(key):
            if key not in image_keys:
                image_keys.append(key)
                if self.images[key][1] == "image/webp":
                    textures.append({"sampler": 0, "extensions": {"EXT_texture_webp": {"source": len(image_keys) - 1}}})
                else:
                    textures.append({"sampler": 0, "source": len(image_keys) - 1})
            return image_keys.index(key)

        materials = []
        uses_clearcoat = False
        for name in used:
            spec = self.materials[name]
            pbr = {"baseColorFactor": list(spec.get("color", (1, 1, 1, 1))),
                   "metallicFactor": spec.get("metal", 0.0),
                   "roughnessFactor": spec.get("rough", 0.5)}
            if "color_tex" in spec:
                pbr["baseColorTexture"] = {"index": texture(spec["color_tex"])}
            if "mr_tex" in spec:
                pbr["metallicRoughnessTexture"] = {"index": texture(spec["mr_tex"])}
            m = {"name": spec.get("label", name), "pbrMetallicRoughness": pbr}
            if "normal_tex" in spec:
                m["normalTexture"] = {"index": texture(spec["normal_tex"]), "scale": spec.get("normal_scale", 1.0)}
            if "emissive" in spec:
                m["emissiveFactor"] = list(spec["emissive"])
            if "emissive_tex" in spec:
                # masca lampilor; stinsa implicit (factor 0), cardul o aprinde
                m["emissiveTexture"] = {"index": texture(spec["emissive_tex"])}
            if "extras" in spec:
                m["extras"] = spec["extras"]
            if spec.get("double"):
                m["doubleSided"] = True
            if "clearcoat" in spec:
                uses_clearcoat = True
                cc = {"clearcoatFactor": spec["clearcoat"],
                      "clearcoatRoughnessFactor": spec.get("clearcoat_rough", 0.05)}
                if "clearcoat_tex" in spec:
                    cc["clearcoatTexture"] = {"index": texture(spec["clearcoat_tex"])}
                m["extensions"] = {"KHR_materials_clearcoat": cc}
            materials.append(m)

        mesh_names = list(self.meshes)
        meshes = []
        stats = {"triangles": 0, "vertices": 0}
        for mname in mesh_names:
            prims = []
            for mat, prim in self.meshes[mname].items():
                pos, nrm, uv, idx = prim.arrays()
                attrs = {"POSITION": accessor(pos.astype(np.float32), "VEC3", minmax=True),
                         "NORMAL": accessor(nrm.astype(np.float32), "VEC3")}
                if uv is not None:
                    attrs["TEXCOORD_0"] = accessor(uv.astype(np.float32), "VEC2")
                ind = accessor(idx.astype(np.uint32).ravel(), "SCALAR", comp=5125, target=34963)
                prims.append({"attributes": attrs, "indices": ind, "material": used.index(mat), "mode": 4})
                stats["triangles"] += len(idx)
                stats["vertices"] += len(pos)
            meshes.append({"name": mname, "primitives": prims})

        images = []
        for key in image_keys:
            data, mime = self.images[key]
            images.append({"name": key, "mimeType": mime, "bufferView": view(data)})

        nodes = [dict(n, mesh=mesh_names.index(n["mesh"])) for n in self.nodes]
        nodes.append({"name": "Opel Astra H Caravan", "children": list(range(len(nodes)))})
        gltf = {
            "asset": {"version": "2.0", "generator": "vehicle_manager astra_caravan", "copyright": credit},
            "scene": 0,
            "scenes": [{"name": "Opel Astra H Caravan", "nodes": [len(nodes) - 1]}],
            "nodes": nodes,
            "meshes": meshes,
            "materials": materials,
            "accessors": accessors,
            "bufferViews": views,
            "buffers": [{"byteLength": offset}],
        }
        if textures:
            gltf["textures"] = textures
            gltf["images"] = images
            gltf["samplers"] = [{"magFilter": 9729, "minFilter": 9987, "wrapS": 10497, "wrapT": 10497}]
        used_ext = []
        if uses_clearcoat:
            used_ext.append("KHR_materials_clearcoat")
        if any(mime == "image/webp" for _, mime in self.images.values()):
            used_ext.append("EXT_texture_webp")
            gltf["extensionsRequired"] = ["EXT_texture_webp"]
        if used_ext:
            gltf["extensionsUsed"] = used_ext

        binary = b"".join(blobs)
        js = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
        js += b" " * ((-len(js)) % 4)
        total = 12 + 8 + len(js) + 8 + len(binary)
        with Path(path).open("wb") as fh:
            fh.write(struct.pack("<III", 0x46546C67, 2, total))
            fh.write(struct.pack("<II", len(js), 0x4E4F534A))
            fh.write(js)
            fh.write(struct.pack("<II", len(binary), 0x004E4942))
            fh.write(binary)
        stats["bytes"] = total
        return stats

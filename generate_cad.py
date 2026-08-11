#!/usr/bin/env python3
"""
Parametric Enclosure Generator for Camel Telemetry V1
Author: S. Alnuaimi
Notes: Basic script to quickly block out internal component spacing
       and double-wall bounding boxes before exporting to GLB.
"""

import os
import trimesh
import numpy as np

LENGTH_MM = 120.0
WIDTH_MM = 80.0
HEIGHT_MM = 50.0
WALL_THICKNESS = 2.0
AIR_GAP = 2.0


def mm_to_m(val):
    return val / 1000.0


def build_enclosure():
    print("Building parametric geometry...")

    l_ext = mm_to_m(LENGTH_MM)
    w_ext = mm_to_m(WIDTH_MM)
    h_ext = mm_to_m(HEIGHT_MM)

    outer_box = trimesh.creation.box(extents=[l_ext, w_ext, h_ext])

    offset = mm_to_m(WALL_THICKNESS * 2)
    inner_box = trimesh.creation.box(
        extents=[l_ext - offset, w_ext - offset, h_ext - offset]
    )

    shell = outer_box.difference(inner_box, engine="manifold")
    shell.visual = trimesh.visual.TextureVisuals(
        material=trimesh.visual.material.PBRMaterial(
            baseColorFactor=[235, 235, 235, 90],
            alphaMode="BLEND",
        )
    )

    core_l = l_ext - mm_to_m((WALL_THICKNESS + AIR_GAP) * 2)
    core_w = w_ext - mm_to_m((WALL_THICKNESS + AIR_GAP) * 2)
    core_h = h_ext - mm_to_m((WALL_THICKNESS + AIR_GAP) * 2)

    core = trimesh.creation.box(extents=[core_l, core_w, core_h])
    core_cavity = trimesh.creation.box(
        extents=[core_l - mm_to_m(4), core_w - mm_to_m(4), core_h - mm_to_m(4)]
    )
    inner_housing = core.difference(core_cavity, engine="manifold")
    inner_housing.visual = trimesh.visual.TextureVisuals(
        material=trimesh.visual.material.PBRMaterial(
            baseColorFactor=[45, 45, 45, 255],
            alphaMode="OPAQUE",
        )
    )

    scene = trimesh.Scene()
    scene.add_geometry(shell, node_name="outer_shell_ASA")
    scene.add_geometry(inner_housing, node_name="inner_core_PETG")

    os.makedirs("cad", exist_ok=True)
    out_file = "cad/enclosure_v1.glb"
    scene.export(out_file)
    print(f"Exported: {out_file}")

    return scene


if __name__ == "__main__":
    build_enclosure()

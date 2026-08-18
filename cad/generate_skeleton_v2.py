"""
generate_skeleton_v2.py

Parametric generator for the V2 enclosure: a 3D-printed ABS "skeleton" frame
wrapped in polyester/fabric mesh, replacing the sealed double-walled V1
housing.

Design rationale (ties to README > Mechanical Enclosure & CAD Architecture,
V1 Limitations):

  - Thermal Trapping   -> V1's sealed dead-air gap is replaced with an open
                          lattice skeleton. No solid outer shell means no
                          trapped convection layer around the ESP32.
  - Vibration Fatigue  -> PCB is not screwed directly to rigid ribs. It sits
                          on four compliant standoffs with a short vertical
                          flex neck, isolating solder joints from
                          low-frequency gait-driven vibration.
  - Fastener Creep     -> No self-tapping threads into ABS. Heat-set insert
                          bosses (brass insert ID configurable) are used at
                          every fastening point instead.
  - Battery Safety     -> Battery bay is a separate cage at the frame's
                          leading edge (max airflow exposure), physically
                          isolated from the ESP32/PCB bay by an open rib,
                          not enclosed insulation.
  - Mesh attachment    -> The skeleton's outer ring has a continuous groove
                          + periodic tab slots sized for polyester mesh
                          edge-binding (drawstring or bar-tack style),
                          rather than trying to 3D print the mesh itself.

Mesh is a textile, not a printable geometry -- this script generates the
ABS skeleton only. Mesh wraps over it and is secured through the groove.

Requires: cadquery (`pip install cadquery`)
Output: skeleton_v2.step, skeleton_v2.stl in ./output/
"""

import cadquery as cq
import os

# ---------------------------------------------------------------------------
# Parameters (mm unless noted) - tune these for your camel harness geometry
# ---------------------------------------------------------------------------
FRAME_LENGTH = 90.0          # overall skeleton length (long axis, along spine)
FRAME_WIDTH = 55.0           # overall skeleton width
FRAME_HEIGHT = 22.0          # overall skeleton height
RIB_THICKNESS = 3.2          # structural rib wall thickness (ABS, ~2 perimeters @ 0.4mm nozzle x4)
RIB_COUNT = 5                # number of cross-ribs along the length
LATTICE_OPEN_FRACTION = 0.45 # fraction of side area left open for airflow

MESH_GROOVE_DEPTH = 1.5
MESH_GROOVE_WIDTH = 2.0
MESH_TAB_COUNT = 8           # tab slots around perimeter for mesh bar-tacking

PCB_LENGTH = 40.0
PCB_WIDTH = 28.0
PCB_STANDOFF_HEIGHT = 6.0
PCB_STANDOFF_FLEX_NECK_D = 2.2   # thin flexible neck diameter - decouples PCB from frame vibration
PCB_STANDOFF_BASE_D = 5.0
INSERT_HOLE_D = 3.2              # bore for M3 brass heat-set insert (adjust to insert spec)
INSERT_DEPTH = 4.5

BATTERY_BAY_LENGTH = 30.0
BATTERY_BAY_WIDTH = 20.0
BATTERY_BAY_HEIGHT = 10.0
BATTERY_VENT_SLOT_COUNT = 4

OUTPUT_DIR = "./output"


def build_base_frame():
    """Outer skeleton ring with mesh-attachment groove."""
    outer = (
        cq.Workplane("XY")
        .rect(FRAME_LENGTH, FRAME_WIDTH)
        .extrude(FRAME_HEIGHT)
    )
    inner_cut = (
        cq.Workplane("XY")
        .rect(FRAME_LENGTH - 2 * RIB_THICKNESS, FRAME_WIDTH - 2 * RIB_THICKNESS)
        .extrude(FRAME_HEIGHT)
    )
    frame = outer.cut(inner_cut)

    # Mesh attachment groove around the top perimeter
    groove_outer = (
        cq.Workplane("XY")
        .workplane(offset=FRAME_HEIGHT - MESH_GROOVE_DEPTH - 1.0)
        .rect(FRAME_LENGTH + 0.1, FRAME_WIDTH + 0.1)
        .extrude(MESH_GROOVE_DEPTH)
    )
    groove_inner = (
        cq.Workplane("XY")
        .workplane(offset=FRAME_HEIGHT - MESH_GROOVE_DEPTH - 1.0)
        .rect(
            FRAME_LENGTH - 2 * MESH_GROOVE_WIDTH,
            FRAME_WIDTH - 2 * MESH_GROOVE_WIDTH,
        )
        .extrude(MESH_GROOVE_DEPTH)
    )
    groove = groove_outer.cut(groove_inner)
    frame = frame.cut(groove)

    return frame


def add_lattice_ribs(frame):
    """Cut open lattice windows into the long sides for passive airflow."""
    window_h = FRAME_HEIGHT * 0.5
    window_w = (FRAME_LENGTH / RIB_COUNT) * LATTICE_OPEN_FRACTION

    for side_y in (-FRAME_WIDTH / 2, FRAME_WIDTH / 2):
        for i in range(RIB_COUNT):
            x = -FRAME_LENGTH / 2 + (i + 0.5) * (FRAME_LENGTH / RIB_COUNT)
            window = (
                cq.Workplane("XY")
                .workplane(offset=FRAME_HEIGHT * 0.25)
                .center(x, side_y)
                .rect(window_w, RIB_THICKNESS + 2)
                .extrude(window_h)
            )
            frame = frame.cut(window)
    return frame


def add_mesh_tab_slots(frame):
    """Periodic slots in the outer wall for mesh bar-tack / drawstring anchoring."""
    slot_w = 2.5
    slot_h = 4.0
    perimeter_positions = []
    for i in range(MESH_TAB_COUNT):
        angle_frac = i / MESH_TAB_COUNT
        # simple rectangular perimeter distribution (not true arc-length,
        # fine for a boxy frame -- refine if you move to a rounded profile)
        x = -FRAME_LENGTH / 2 + angle_frac * FRAME_LENGTH
        y = FRAME_WIDTH / 2
        slot = (
            cq.Workplane("XY")
            .workplane(offset=FRAME_HEIGHT - MESH_GROOVE_DEPTH - 1.0 - slot_h / 2)
            .center(x, y)
            .rect(slot_w, RIB_THICKNESS + 1)
            .extrude(slot_h)
        )
        frame = frame.cut(slot)
    return frame


def add_pcb_standoffs(frame):
    """Four compliant standoffs (rigid base + thin flex neck + insert boss)
    to vibration-isolate the PCB from the frame."""
    positions = [
        (PCB_LENGTH / 2 - 3, PCB_WIDTH / 2 - 3),
        (PCB_LENGTH / 2 - 3, -(PCB_WIDTH / 2 - 3)),
        (-(PCB_LENGTH / 2 - 3), PCB_WIDTH / 2 - 3),
        (-(PCB_LENGTH / 2 - 3), -(PCB_WIDTH / 2 - 3)),
    ]
    for x, y in positions:
        base = (
            cq.Workplane("XY")
            .workplane(offset=0)
            .center(x, y)
            .circle(PCB_STANDOFF_BASE_D / 2)
            .extrude(2.0)
        )
        neck = (
            cq.Workplane("XY")
            .workplane(offset=2.0)
            .center(x, y)
            .circle(PCB_STANDOFF_FLEX_NECK_D / 2)
            .extrude(PCB_STANDOFF_HEIGHT - 2.0 - INSERT_DEPTH)
        )
        boss = (
            cq.Workplane("XY")
            .workplane(offset=PCB_STANDOFF_HEIGHT - INSERT_DEPTH)
            .center(x, y)
            .circle(PCB_STANDOFF_BASE_D / 2)
            .extrude(INSERT_DEPTH)
        )
        insert_bore = (
            cq.Workplane("XY")
            .workplane(offset=PCB_STANDOFF_HEIGHT - INSERT_DEPTH)
            .center(x, y)
            .circle(INSERT_HOLE_D / 2)
            .extrude(INSERT_DEPTH)
        )
        standoff = base.union(neck).union(boss).cut(insert_bore)
        frame = frame.union(standoff)
    return frame


def add_battery_bay(frame):
    """Isolated, vented battery cage at the leading edge of the frame."""
    bay_x = FRAME_LENGTH / 2 - BATTERY_BAY_LENGTH / 2 - RIB_THICKNESS
    cage = (
        cq.Workplane("XY")
        .center(bay_x, 0)
        .rect(BATTERY_BAY_LENGTH, BATTERY_BAY_WIDTH)
        .extrude(BATTERY_BAY_HEIGHT)
    )
    cage_inner = (
        cq.Workplane("XY")
        .center(bay_x, 0)
        .rect(BATTERY_BAY_LENGTH - 2 * RIB_THICKNESS, BATTERY_BAY_WIDTH - 2 * RIB_THICKNESS)
        .extrude(BATTERY_BAY_HEIGHT)
    )
    cage = cage.cut(cage_inner)

    # Vent slots in the top face
    for i in range(BATTERY_VENT_SLOT_COUNT):
        y = -BATTERY_BAY_WIDTH / 2 + (i + 0.5) * (BATTERY_BAY_WIDTH / BATTERY_VENT_SLOT_COUNT)
        vent = (
            cq.Workplane("XY")
            .workplane(offset=BATTERY_BAY_HEIGHT - 1.5)
            .center(bay_x, y)
            .rect(BATTERY_BAY_LENGTH - 2 * RIB_THICKNESS - 2, 2.0)
            .extrude(1.5)
        )
        cage = cage.cut(vent)

    return frame.union(cage)


def build():
    frame = build_base_frame()
    frame = add_lattice_ribs(frame)
    frame = add_mesh_tab_slots(frame)
    frame = add_pcb_standoffs(frame)
    frame = add_battery_bay(frame)
    return frame


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model = build()
    cq.exporters.export(model, os.path.join(OUTPUT_DIR, "skeleton_v2.step"))
    cq.exporters.export(model, os.path.join(OUTPUT_DIR, "skeleton_v2.stl"))
    print("Exported skeleton_v2.step and skeleton_v2.stl to", OUTPUT_DIR)

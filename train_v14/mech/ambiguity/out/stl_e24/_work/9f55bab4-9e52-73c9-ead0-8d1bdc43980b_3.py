from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 5.0
wall_thickness = 1.0
slot_length = 40.0
slot_width = 8.0
hole_diameter = 6.5
hole_offset = 5.0
edge_fillet_radius = 0.8

base = Box(plate_width, plate_depth, plate_thickness)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness * 3, both=True)
base = base - slot_bp.part

hole_positions = [
    (-plate_width/2 + hole_offset, -plate_depth/2 + hole_offset),
    ( plate_width/2 - hole_offset, -plate_depth/2 + hole_offset),
    (-plate_width/2 + hole_offset,  plate_depth/2 - hole_offset),
    ( plate_width/2 - hole_offset,  plate_depth/2 - hole_offset),
]
for x, y in hole_positions:
    base = base - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 3)

vertical_edges = base.edges().filter_by(Axis.Z)
base = fillet(vertical_edges, edge_fillet_radius)

part = base
part.name = "shelled_plate_with_slot_and_holes"
export_step(part, "output.step")
from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
wall_thickness = 1.0
edge_fillet_radius = 0.8
hole_diameter = 6.5
hole_offset = 5.0
slot_length = 40.0
slot_width = 8.0

solid_body = Box(plate_length, plate_width, plate_thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, edge_fillet_radius)

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness * 2)
slot_solid = slot_bp.part
solid_body = solid_body - slot_solid

part = solid_body
part.name = "shelled_plate_with_holes_and_slot"
export_step(part, "output.step")
from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 8.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 5.0
fillet_radius = 2.0
chamfer_distance = 0.5
hole_diameter = 7.0
hole_spacing = 40.0
slot_length = 40.0
slot_width = 6.0
slot_offset_y = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

pocket = Pos(0, 0, plate_thickness) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)

for x, y in [(0, slot_offset_y), (0, -slot_offset_y)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness + 1)

part = solid_body
part.name = "plate_with_pocket_holes_slots"
export_step(part, "output.step")
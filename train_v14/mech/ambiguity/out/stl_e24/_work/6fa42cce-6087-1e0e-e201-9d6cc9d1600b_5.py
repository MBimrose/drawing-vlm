from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
corner_radius = 4.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 3.0
slot_length = 60.0
slot_width = 3.0
hole_diameter = 5.0
hole_offset_x = 20.0
hole_offset_y = 10.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

slot = Pos(0, 0, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - slot

hole_positions = [
    (hole_offset_x, hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (hole_offset_x, -hole_offset_y),
    (-hole_offset_x, -hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

part = solid_body
part.name = "plate_with_pocket_slot_holes"
export_step(part, "output.step")
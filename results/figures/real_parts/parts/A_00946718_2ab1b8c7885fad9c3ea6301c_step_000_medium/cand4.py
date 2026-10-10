from build123d import *

body_length = 80.0
body_width = 30.0
body_height = 15.0
wall_thickness = 3.0
central_bore_diameter = 20.0
slot_width = 8.0
slot_length = 25.0
slot_offset = 10.0
fillet_radius = 2.7

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(body_length, body_width)
    extrude(amount=body_height)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

solid_body = solid_body - Cylinder(central_bore_diameter/2, body_height * 2)

slot_x = body_length/2 - slot_offset
solid_body = solid_body - Pos(slot_x, 0, 0) * Cylinder(slot_width/2, body_height * 2)
solid_body = solid_body - Pos(-slot_x, 0, 0) * Cylinder(slot_width/2, body_height * 2)

part = solid_body
part.name = "body_with_bore_and_slots"
export_step(part, "output.step")
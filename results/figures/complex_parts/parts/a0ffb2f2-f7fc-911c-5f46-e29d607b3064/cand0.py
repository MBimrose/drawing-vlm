from build123d import *

shaft_diameter = 10.0
shaft_length = 55.0
flange_diameter = 30.0
flange_thickness = 10.0
hole_diameter = 8.0
hole_depth = 12.0
slot_width = 4.0
slot_depth = 2.0
chamfer_size = 0.5

shaft = Pos(0, 0, shaft_length / 2) * Cylinder(shaft_diameter / 2, shaft_length)
flange = Pos(0, 0, shaft_length + flange_thickness / 2) * Cylinder(flange_diameter / 2, flange_thickness)
solid_body = shaft + flange

hole = Pos(0, 0, shaft_length + flange_thickness - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)
solid_body = solid_body - hole

slot = Pos(0, 0, shaft_length / 2) * Box(slot_width, slot_depth, shaft_length)
solid_body = solid_body - slot

solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "shaft_with_flange"
export_step(part, "output.step")
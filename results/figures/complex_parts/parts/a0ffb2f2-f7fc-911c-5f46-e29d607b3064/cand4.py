from build123d import *

shaft_diameter = 10.0
shaft_length = 55.0
head_diameter = 30.0
head_thickness = 10.0
chamfer_size = 1.0
hole_diameter = 8.0
slot_width = 4.0
slot_depth = 2.0

shaft = Pos(0, 0, shaft_length/2) * Cylinder(shaft_diameter/2, shaft_length)
head = Pos(0, 0, shaft_length + head_thickness/2) * Cylinder(head_diameter/2, head_thickness)
solid_body = shaft + head

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

hole = Pos(0, 0, shaft_length + head_thickness/2) * Cylinder(hole_diameter/2, head_thickness)
solid_body = solid_body - hole

slot = Pos(0, 0, shaft_length + head_thickness/2) * Box(slot_width, slot_depth, head_thickness)
solid_body = solid_body - slot

part = solid_body
part.name = "shaft_with_head"
export_step(part, "output.step")
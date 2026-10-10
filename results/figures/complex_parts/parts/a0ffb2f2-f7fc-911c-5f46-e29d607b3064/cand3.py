from build123d import *

shank_diameter = 10.0
shank_length = 45.0
head_diameter = 30.0
head_thickness = 10.0
hole_diameter = 8.0
slot_width = 4.0
slot_length = 12.0
chamfer_size = 1.0

shank = Pos(0, 0, shank_length / 2) * Cylinder(shank_diameter / 2, shank_length)
head = Pos(0, 0, shank_length + head_thickness / 2) * Cylinder(head_diameter / 2, head_thickness)
solid_body = shank + head

hole = Pos(0, 0, shank_length + head_thickness / 2) * Cylinder(hole_diameter / 2, head_thickness)
solid_body = solid_body - hole

slot = Pos(0, 0, shank_length + head_thickness / 2) * Box(slot_length, slot_width, head_thickness)
solid_body = solid_body - slot

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "pin_with_head"
export_step(part, "output.step")
from build123d import *

bracket_length = 60
bracket_width = 40
bracket_thickness = 5
rib_height = 8
rib_thickness = 3
rib_length = 40
slot_length = 20
slot_width = 4
slot_offset_x = -bracket_length/2 + 5 + slot_length/2
slot_offset_y = bracket_width/2 - 10 - slot_width/2
hole_diameter = 5
hole_center_x = 0
hole_center_y = bracket_width/2
chamfer_dist = 0.5

base = Box(bracket_length, bracket_width, bracket_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_dist)

rib = Pos(0, bracket_width/2 + rib_thickness/2, 0) * Box(rib_length, rib_thickness, rib_height)
base = base + rib

slot = Pos(slot_offset_x, slot_offset_y, 0) * Box(slot_length, slot_width, bracket_thickness)
base = base - slot

hole = Pos(hole_center_x, hole_center_y, 0) * Cylinder(hole_diameter/2, bracket_thickness)
base = base - hole

part = base
part.name = "bracket"
export_step(part, "output.step")
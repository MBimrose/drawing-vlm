from build123d import *

base_length = 80.0
base_width = 30.0
base_thickness = 8.0
rib_height = 4.0
rib_width = 12.0
rib_thickness = 2.0
hole_diameter = 5.0
hole_offset_x = 30.0
hole_offset_z = 4.0
notch_width = 6.0
notch_depth = 3.0

base = Box(base_length, base_width, base_thickness)
rib = Pos(0, 0, base_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)
result = base + rib

hole = Pos(hole_offset_x - base_length/2, -base_width/2, hole_offset_z - base_thickness/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, base_width)
result = result - hole

notch = Pos(base_length/2 - notch_depth/2, base_width/2 - notch_depth/2, 0) * Box(notch_depth, notch_depth, notch_width)
result = result - notch

part = result
part.name = "base_with_rib_hole_notch"
export_step(part, "output.step")
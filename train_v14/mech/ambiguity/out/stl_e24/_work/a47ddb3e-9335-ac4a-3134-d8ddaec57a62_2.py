from build123d import *

bracket_width = 60.0
bracket_height = 40.0
bracket_thickness = 5.0
rib_width = 50.0
rib_height = 8.0
rib_thickness = 3.0
hole_diameter = 5.0
notch_width = 20.0
notch_height = 4.0
notch_offset_x = -bracket_width/2 + 5.0
notch_offset_y = bracket_height/2 - 10.0

base = Box(bracket_width, bracket_height, bracket_thickness)
notch = Pos(notch_offset_x, notch_offset_y, 0) * Box(notch_width, notch_height, bracket_thickness)
base = base - notch

rib = Pos(0, bracket_height/2 + rib_thickness/2, 0) * Box(rib_width, rib_thickness, rib_height)
hole = Pos(0, bracket_height/2 + rib_thickness/2, 0) * Cylinder(hole_diameter/2, rib_height)
rib = rib - hole

part = base + rib
part.name = "bracket_with_rib"
export_step(part, "output.step")
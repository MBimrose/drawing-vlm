from build123d import *

width = 60.0
height = 40.0
thickness = 5.0
rib_width = 40.0
rib_height = 8.0
rib_thickness = 3.0
pocket_width = 20.0
pocket_height = 4.0
pocket_offset_y = 5.0
hole_diameter = 5.0
hole_offset_y = 10.0

base = Box(width, height, thickness)
rib = Pos(0, height/2 + rib_thickness/2, 0) * Box(rib_width, rib_thickness, rib_height)
result = base + rib

pocket = Pos(-width/4, height/2 - pocket_offset_y, 0) * Box(pocket_width, pocket_height, thickness)
result = result - pocket

hole = Pos(0, height/2 - hole_offset_y, 0) * Cylinder(hole_diameter/2, thickness)
result = result - hole

part = result
part.name = "plate_with_rib_pocket_and_hole"
export_step(part, "output.step")
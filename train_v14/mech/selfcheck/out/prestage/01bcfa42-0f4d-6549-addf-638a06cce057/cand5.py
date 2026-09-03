from build123d import *

plate_width = 80
plate_depth = 60
plate_thickness = 5
hole_diameter = 6
hole_depth = 2

base = Box(plate_width, plate_depth, plate_thickness)
hole = Pos(0, 0, plate_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
part = base - hole
part.name = "plate_with_hole"
export_step(part, "output.step")
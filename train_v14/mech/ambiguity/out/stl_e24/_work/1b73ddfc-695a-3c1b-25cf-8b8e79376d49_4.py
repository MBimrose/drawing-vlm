from build123d import *

plate_width = 60
plate_height = 40
plate_thickness = 8
hole_diameter = 4
cbore_diameter = 5
cbore_depth = 4

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = solid_body - Cylinder(hole_diameter/2, plate_thickness)
solid_body = solid_body - Pos(0, 0, -plate_thickness/2 + cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)

part = solid_body
part.name = "plate_with_cbore_hole"
export_step(part, "output.step")
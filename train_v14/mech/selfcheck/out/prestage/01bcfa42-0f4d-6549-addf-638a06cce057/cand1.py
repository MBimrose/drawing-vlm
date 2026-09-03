from build123d import *

plate_width=80
plate_height=60
plate_thickness=5

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Cylinder(3, 2)

part = solid_body
part.name = "plate_with_hole"
export_step(part, "output.step")
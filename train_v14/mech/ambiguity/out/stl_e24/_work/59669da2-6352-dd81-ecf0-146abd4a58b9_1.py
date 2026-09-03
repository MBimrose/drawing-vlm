from build123d import *

base_length = 80.0
base_width = 30.0
base_thickness = 5.0
shoulder_length = 20.0
shoulder_height = 8.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 10.0
hole_rows = 2
hole_cols = 3
fillet_radius = 2.0

base = Box(base_length, base_width, base_thickness)
shoulder = Pos(base_length/2 - shoulder_length/2, 0, base_thickness/2 + shoulder_height/2) * Box(shoulder_length, base_width, shoulder_height)
solid_body = base + shoulder

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "base_with_shoulder_and_holes"
export_step(part, "output.step")
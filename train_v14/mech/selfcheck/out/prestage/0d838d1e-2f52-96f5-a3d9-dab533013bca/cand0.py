from build123d import *

plate_length = 100.0
plate_width = 60.0
plate_thickness = 8.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 4.0
hole_diameter = 6.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 4
rib_width = 10.0
rib_thickness = 4.0
rib_spacing = 30.0

result = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
result = result - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib1 = Pos(0, 0, -plate_thickness/2 - rib_thickness/2) * Box(rib_width, rib_thickness, rib_thickness)
result = result + rib1

rib2 = Pos(-rib_spacing, 0, -plate_thickness/2 - rib_thickness/2) * Box(rib_width, rib_thickness, rib_thickness)
result = result + rib2

rib3 = Pos(rib_spacing, 0, -plate_thickness/2 - rib_thickness/2) * Box(rib_width, rib_thickness, rib_thickness)
result = result + rib3

part = result
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")
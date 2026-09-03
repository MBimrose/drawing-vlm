from build123d import *

plate_length = 100.0
plate_width = 60.0
plate_thickness = 8.0
pocket_length = 30.0
pocket_width = 20.0
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

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)
        result = result - hole

rib_positions = [-plate_length/2 + rib_spacing, 0, plate_length/2 - rib_spacing]
for x in rib_positions:
    rib = Pos(x, 0, -plate_thickness/2 - rib_thickness/2) * Box(rib_width, rib_thickness, rib_thickness)
    result = result + rib

part = result
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")
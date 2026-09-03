from build123d import *

plate_width = 80.0
plate_height = 100.0
plate_thickness = 5.0
rib_width = 30.0
rib_height = 30.0
rib_thickness = 3.0
pocket_width = 40.0
pocket_height = 30.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 4
chamfer_size = 1.0

base = Box(plate_width, plate_height, plate_thickness)
rib = Pos(0, 0, plate_thickness/2 - rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
result = base + rib

pocket = Box(pocket_width, pocket_height, plate_thickness + 1)
result = result - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_rib_pocket_holes"
export_step(part, "output.step")
from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 12.0
groove_width = 12.0
groove_depth = 4.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 3
hole_cols = 4
chamfer_size = 1.0

base = Box(plate_length, plate_width, plate_thickness)
groove = Pos(0, 0, plate_thickness/2 - groove_depth/2) * Box(groove_width, plate_width, groove_depth)
result = base - groove

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_groove_and_holes"
export_step(part, "output.step")
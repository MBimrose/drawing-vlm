from build123d import *

plate_length = 100
plate_width = 80
plate_thickness = 12
groove_width = 10
groove_depth = 4
hole_diameter = 5
hole_spacing_x = 20
hole_spacing_y = 20
hole_rows = 3
hole_cols = 4
boss_diameter = 20
boss_height = 8
chamfer_size = 1

base = Box(plate_length, plate_width, plate_thickness)
boss = Cylinder(boss_diameter / 2, boss_height)
result = base + boss

groove = Pos(0, 0, plate_thickness / 2 - groove_depth / 2) * Box(groove_width, plate_length, groove_depth)
result = result - groove

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness + boss_height + 10)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_groove_and_holes"
export_step(part, "output.step")
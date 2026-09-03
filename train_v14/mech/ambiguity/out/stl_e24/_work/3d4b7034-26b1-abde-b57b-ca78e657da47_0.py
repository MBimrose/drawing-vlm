from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
boss_diameter = 40.0
boss_height = 4.0
hole_diameter = 8.0
hole_spacing_x = 40.0
hole_spacing_y = 30.0
hole_rows = 2
hole_cols = 2
chamfer_size = 1.0
rib_width = 10.0
rib_height = 3.0
rib_length = plate_length - 10.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0

result = Box(plate_length, plate_width, plate_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)
result = result + Pos(0, 0, plate_thickness) * Cylinder(boss_diameter / 2, boss_height)
result = result + Pos(0, 0, plate_thickness) * Box(rib_length, rib_width, rib_height)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness + boss_height + rib_height + 10)

result = result - Pos(0, 0, plate_thickness + boss_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)

part = result
part.name = "plate_with_boss_rib_holes_pocket"
export_step(part, "output.step")
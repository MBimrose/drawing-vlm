from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
boss_diameter = 20.0
boss_height = 4.0
rib_width = 4.0
rib_height = 3.0
rib_offset = 15.0
pocket_diameter = 30.0
pocket_depth = 2.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 30.0
hole_rows = 2
hole_cols = 4
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)
boss = Cylinder(boss_diameter / 2, boss_height)
rib1 = Pos(-plate_length / 2 + rib_offset, 0, 0) * Box(rib_width, plate_width - 2 * rib_offset, rib_height)
rib2 = Pos(plate_length / 2 - rib_offset, 0, 0) * Box(rib_width, plate_width - 2 * rib_offset, rib_height)

result = base + boss + rib1 + rib2

pocket = Pos(0, 0, plate_thickness / 2 - pocket_depth / 2) * Cylinder(pocket_diameter / 2, pocket_depth)
result = result - pocket

hole_h = plate_thickness + boss_height + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, hole_h)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_ribs_pockets"
export_step(part, "output.step")
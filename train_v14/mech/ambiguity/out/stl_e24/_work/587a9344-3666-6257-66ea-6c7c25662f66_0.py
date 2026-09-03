from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 10.0
boss_diameter = 30.0
boss_height = 12.0
hole_diameter = 8.0
hole_depth = 8.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 2
chamfer_size = 1.0
rib_width = 5.0
rib_length = 40.0
rib_height = 2.0

base = Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness) * Cylinder(boss_diameter / 2, boss_height)
rib_left = Pos(-plate_length / 2 + rib_width / 2, 0, plate_thickness) * Box(rib_width, rib_length, rib_height)
rib_right = Pos(plate_length / 2 - rib_width / 2, 0, plate_thickness) * Box(rib_width, rib_length, rib_height)

solid_body = base + boss + rib_left + rib_right

hole_r = hole_diameter / 2
hole_z = plate_thickness + boss_height - hole_depth / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, hole_z) * Cylinder(hole_r, hole_depth)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_boss_ribs_and_holes"
export_step(part, "output.step")
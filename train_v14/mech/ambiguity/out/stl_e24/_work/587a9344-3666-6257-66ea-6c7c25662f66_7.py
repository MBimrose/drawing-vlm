from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 10.0
boss_diameter = 30.0
boss_height = 12.0
hole_diameter = 8.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 2
chamfer_size = 1.0
rib_height = 5.0
rib_width = 5.0
rib_spacing = 20.0

base = Box(plate_width, plate_depth, plate_thickness)
boss = Pos(0, 0, plate_thickness) * Cylinder(boss_diameter / 2, boss_height)
result = base + boss

start_x = -((hole_cols - 1) * hole_spacing_x) / 2
start_y = -((hole_rows - 1) * hole_spacing_y) / 2
for i in range(hole_cols):
    for j in range(hole_rows):
        px = start_x + i * hole_spacing_x
        py = start_y + j * hole_spacing_y
        result = result - Pos(px, py, plate_thickness + boss_height / 2) * Cylinder(hole_diameter / 2, boss_height + 10)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

rib1 = Pos(0, -rib_spacing / 2, -rib_height / 2) * Box(plate_width - 10, rib_width, rib_height)
rib2 = Pos(0, rib_spacing / 2, -rib_height / 2) * Box(plate_width - 10, rib_width, rib_height)
result = result + rib1 + rib2

part = result
part.name = "plate_with_boss_holes_and_ribs"
export_step(part, "output.step")
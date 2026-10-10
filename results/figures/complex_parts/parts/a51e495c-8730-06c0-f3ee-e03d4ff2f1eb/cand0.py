from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 6.0
boss_radius = 12.0
boss_height = 12.0
hole_diameter = 5.0
hole_spacing = 10.0
hole_count = 5
fillet_radius = 2.0
rib_width = 4.0
rib_height = 2.0
rib_spacing = 12.0
pocket_depth = 4.0
pocket_margin = 10.0

base = Box(plate_length, plate_width, plate_thickness)
base = fillet(base.edges(), fillet_radius)

boss = Cylinder(boss_radius, boss_height)
result = base + boss

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, 100)

rib_count_x = int((plate_length - 2 * rib_spacing) / rib_spacing) + 1
rib_count_y = int((plate_width - 2 * rib_spacing) / rib_spacing) + 1
for i in range(rib_count_x):
    for j in range(rib_count_y):
        x = (i - (rib_count_x - 1) / 2) * rib_spacing
        y = (j - (rib_count_y - 1) / 2) * rib_spacing
        result = result + Pos(x, y, plate_thickness / 2 + rib_height / 2) * Box(rib_width, rib_width, rib_height)

pocket = Pos(0, 0, -plate_thickness / 2 + pocket_depth / 2) * Box(plate_length - 2 * pocket_margin, plate_width - 2 * pocket_margin, pocket_depth)
result = result - pocket

part = result
part.name = "plate_with_boss_holes_ribs_pocket"
export_step(part, "output.step")
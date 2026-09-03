from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 3.0
corner_fillet_radius = 1.5
hole_diameter = 3.2
hole_spacing_x = 20.0
hole_spacing_y = 20.0
num_holes_x = 3
num_holes_y = 2
rib_thickness = 2.0
rib_height = 2.0
rib_offset = 10.0
pocket_width = 12.0
pocket_depth = 8.0
pocket_height = 2.0
boss_diameter = 6.0
boss_height = 2.0

result = Box(plate_length, plate_width, plate_thickness)
result = fillet(result.edges().filter_by(Axis.Z), corner_fillet_radius)

for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = (i - (num_holes_x - 1) / 2) * hole_spacing_x
        y = (j - (num_holes_y - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness + 1)

rib1 = Pos(0, rib_offset, plate_thickness) * Box(rib_thickness, plate_length - 2 * rib_offset, rib_height)
rib2 = Pos(0, -rib_offset, plate_thickness) * Box(rib_thickness, plate_length - 2 * rib_offset, rib_height)
result = result + rib1 + rib2

pocket = Pos(0, plate_width / 2 - pocket_depth / 2, plate_thickness / 2) * Box(pocket_width, pocket_depth, pocket_height)
result = result - pocket

boss = Pos(0, 0, plate_thickness) * Cylinder(boss_diameter / 2, boss_height)
result = result + boss

part = result
part.name = "plate_with_ribs_pocket_boss"
export_step(part, "output.step")
from build123d import *

plate_width = 60.0
plate_depth = 30.0
plate_thickness = 8.0
boss_radius = 5.0
boss_height = 30.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 3
fillet_radius = 1.5

base = Box(plate_width, plate_depth, plate_thickness)
boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
result = base + boss

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

hole_r = hole_diameter / 2
hole_h = plate_thickness + boss_height + 20
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

part = result
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")
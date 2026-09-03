from build123d import *

base_length = 70.0
base_width = 30.0
base_thickness = 8.0
fillet_radius = 1.5
boss_radius = 5.0
boss_height = 30.0
hole_diameter = 4.0
hole_spacing = 12.0
hole_rows = 2
hole_cols = 3
rib_width = 5.0
rib_height = 4.0
rib_length = base_length - 10.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

boss = Pos(0, 0, base_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
result = base + boss

rib = Pos(0, 0, base_thickness + rib_height/2) * Box(rib_length, rib_width, rib_height)
result = result + rib

start_x = -((hole_cols - 1) * hole_spacing) / 2
start_y = base_width / 2 - 5.0
for i in range(hole_cols):
    for j in range(hole_rows):
        x = start_x + i * hole_spacing
        y = start_y + j * hole_spacing
        hole = Pos(x, y, base_thickness + boss_height/2) * Cylinder(hole_diameter/2, base_thickness + boss_height + 10)
        result = result - hole

part = result
part.name = "base_with_boss_rib_holes"
export_step(part, "output.step")
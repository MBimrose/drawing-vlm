from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 5.0
boss_diameter = 20.0
boss_height = 10.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 4
fillet_radius = 1.5
rib_height = 2.0
rib_width = 5.0
rib_length = bracket_length - 10.0

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)
boss = Pos(0, 0, bracket_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, bracket_thickness + boss_height/2) * Cylinder(hole_diameter/2, bracket_thickness + boss_height + 10)

rib = Pos(0, -bracket_width/2 + rib_width/2 + 5, -rib_height/2) * Box(rib_length, rib_width, rib_height)
result = result + rib

part = result
part.name = "bracket_with_boss_and_rib"
export_step(part, "output.step")
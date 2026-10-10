from build123d import *

bracket_length = 80.0
bracket_width = 30.0
bracket_thickness = 6.0
boss_radius = 12.0
boss_height = 20.0
hole_diameter = 5.0
hole_spacing = 10.0
hole_count = 5
fillet_radius = 2.0
rib_width = 4.0
rib_height = 2.0
rib_spacing = 12.0
pocket_length = 20.0
pocket_width = 10.0
pocket_depth = 3.0

base = Box(bracket_length, bracket_width, bracket_thickness)
base = fillet(base.edges(), fillet_radius)

boss = Cylinder(boss_radius, boss_height)
result = base + boss

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, 100)

rib_count = int((bracket_length - 2 * rib_spacing) / rib_spacing) + 1
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, bracket_thickness / 2 + rib_height / 2) * Box(rib_width, bracket_width, rib_height)
    result = result + rib

pocket = Pos(0, 0, -bracket_thickness / 2 + pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

part = result
part.name = "bracket"
export_step(part, "output.step")
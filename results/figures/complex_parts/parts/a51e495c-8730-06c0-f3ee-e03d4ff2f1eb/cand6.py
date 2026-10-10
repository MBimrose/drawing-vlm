from build123d import *

leaf_length = 80
leaf_width = 30
leaf_thickness = 6
boss_radius = 12
boss_height = 4
hole_diameter = 5
hole_spacing = 10
hole_count = 5
fillet_radius = 2
rib_width = 4
rib_height = 2
rib_spacing = 12
pocket_depth = 4
pocket_margin = 5

base = Box(leaf_length, leaf_width, leaf_thickness)
base = fillet(base.edges(), fillet_radius)

boss = Pos(0, 0, leaf_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
result = base + boss

rib_count = int((leaf_length - 2 * rib_spacing) / rib_spacing) + 1
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, leaf_thickness/2 + rib_height/2) * Box(rib_width, leaf_width - 2 * pocket_margin, rib_height)
    result = result + rib

pocket = Pos(0, 0, leaf_thickness/2 - pocket_depth/2) * Box(leaf_length - 2 * pocket_margin, leaf_width - 2 * pocket_margin, pocket_depth)
result = result - pocket

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    hole = Pos(x, 0, 0) * Cylinder(hole_diameter / 2, 20)
    result = result - hole

part = result
part.name = "leaf_with_boss_ribs_pocket_holes"
export_step(part, "output.step")
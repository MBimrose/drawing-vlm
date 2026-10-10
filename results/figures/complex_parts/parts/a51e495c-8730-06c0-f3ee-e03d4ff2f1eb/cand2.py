from build123d import *

bracket_length = 80.0
bracket_width = 30.0
bracket_thickness = 6.0
boss_radius = 12.0
boss_height = 12.0
hole_diameter = 5.0
hole_spacing = 10.0
hole_count = 5
fillet_radius = 2.0
rib_width = 4.0
rib_thickness = 2.0
rib_spacing = 12.0

base = Box(bracket_length, bracket_width, bracket_thickness)
base = fillet(base.edges(), fillet_radius)

boss = Cylinder(boss_radius, boss_height)

rib = Box(rib_width, rib_thickness, boss_height)
rib_offset_y = boss_radius + rib_thickness / 2
rib_positions = []
for i in range(-2, 3):
    x = i * rib_spacing
    rib_positions.append((x, rib_offset_y))
    rib_positions.append((x, -rib_offset_y))

ribs = Compound([Pos(x, y, 0) * rib for x, y in rib_positions])

result = base + boss + ribs

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, 50)

part = result
part.name = "bracket"
export_step(part, "output.step")
from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 6.0
boss_radius = 12.0
boss_height = 8.0
hole_diameter = 5.0
hole_spacing = 10.0
hole_count = 5
fillet_radius = 2.0
rib_width = 4.0
rib_height = 2.0
rib_spacing = 10.0

base = Box(plate_length, plate_width, plate_thickness)
boss = Cylinder(boss_radius, boss_height)
result = base + boss
result = fillet(result.edges(), fillet_radius)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, plate_thickness + boss_height + 10)

rib_count = int((plate_length - 2 * rib_spacing) / rib_spacing) + 1
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, -plate_thickness / 2 + rib_height / 2) * Box(rib_width, plate_width - 2 * rib_spacing, rib_height)
    result = result + rib

part = result
part.name = "plate_with_boss_and_ribs"
export_step(part, "output.step")
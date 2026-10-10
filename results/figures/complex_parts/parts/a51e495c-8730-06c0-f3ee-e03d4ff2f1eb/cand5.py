from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 6.0
boss_radius = 12.0
boss_height = 15.0
hole_diameter = 5.0
hole_spacing = 10.0
hole_count = 5
fillet_radius = 2.0
slot_length = 20.0
slot_width = 4.0
rib_width = 4.0
rib_height = 8.0
rib_spacing = 12.0

base = Box(leaf_length, leaf_width, leaf_thickness)
base = fillet(base.edges(), fillet_radius)

boss = Cylinder(boss_radius, boss_height)
result = base + boss

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, 100)

slot = Box(slot_length, slot_width, leaf_thickness)
result = result - Pos(-leaf_length / 2 + slot_length / 2, 0, 0) * slot
result = result - Pos(leaf_length / 2 - slot_length / 2, 0, 0) * slot

rib_count = int((leaf_length - 2 * rib_spacing) / rib_spacing) + 1
rib = Box(rib_width, leaf_thickness, rib_height)
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    result = result + Pos(x, leaf_width / 2 - leaf_thickness / 2, 0) * rib
    result = result + Pos(x, -leaf_width / 2 + leaf_thickness / 2, 0) * rib

part = result
part.name = "leaf_with_boss_holes_slots_ribs"
export_step(part, "output.step")
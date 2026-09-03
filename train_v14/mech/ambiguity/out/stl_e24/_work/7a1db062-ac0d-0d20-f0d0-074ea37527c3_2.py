from build123d import *

base_length = 80.0
base_width = 50.0
base_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
through_hole_diameter = 12.0
tapped_hole_diameter = 4.2
tapped_hole_depth = boss_height + 2.0
tapped_hole_offset = boss_diameter / 4.0
slot_width = 6.0
slot_length = 30.0
slot_depth = 8.0
pocket_width = 20.0
pocket_depth = 10.0
pocket_height = 5.0
pocket_offset_x = 15.0

result = Box(base_length, base_width, base_thickness)
result = result + Pos(0, 0, base_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result - Cylinder(through_hole_diameter/2, base_thickness + boss_height + 2)
result = result - Pos(tapped_hole_offset, 0, base_thickness/2 + boss_height - tapped_hole_depth/2) * Cylinder(tapped_hole_diameter/2, tapped_hole_depth)
result = result - Pos(0, 0, base_thickness/2 + boss_height - slot_depth/2) * Box(slot_length, slot_width, slot_depth)
result = result - Pos(pocket_offset_x, 0, base_thickness/2 + boss_height - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)

part = result
part.name = "base_with_boss_and_features"
export_step(part, "output.step")
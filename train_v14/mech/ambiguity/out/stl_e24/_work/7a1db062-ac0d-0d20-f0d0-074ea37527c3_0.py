from build123d import *

base_length = 80.0
base_width = 50.0
base_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
central_hole_diameter = 12.0
set_screw_diameter = 4.2
set_screw_counterbore_diameter = 7.0
set_screw_counterbore_depth = 2.0
set_screw_offset = boss_diameter / 4.0
slot_length = 30.0
slot_width = 6.0
slot_depth = 8.0
chamfer_size = 0.8

base = Pos(0, 0, base_thickness / 2) * Box(base_length, base_width, base_thickness)
boss = Pos(0, 0, base_thickness + boss_height / 2) * Cylinder(boss_diameter / 2.0, boss_height)
result = base + boss

result = result - Pos(0, 0, base_thickness + boss_height / 2) * Cylinder(central_hole_diameter / 2.0, base_thickness + boss_height + 10)

result = result - Pos(0, 0, base_thickness + boss_height - slot_depth / 2) * Box(slot_length, slot_width, slot_depth)

result = result - Pos(set_screw_offset, 0, base_thickness + boss_height / 2) * Cylinder(set_screw_diameter / 2.0, base_thickness + boss_height + 10)

result = result - Pos(set_screw_offset, 0, base_thickness + boss_height - set_screw_counterbore_depth / 2) * Cylinder(set_screw_counterbore_diameter / 2.0, set_screw_counterbore_depth)

part = result
part.name = "base_with_boss_and_holes"
export_step(part, "output.step")
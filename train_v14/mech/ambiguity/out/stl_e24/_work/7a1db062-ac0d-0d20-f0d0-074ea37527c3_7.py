from build123d import *

block_length = 80.0
block_width = 50.0
block_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
through_hole_diameter = 12.0
set_screw_diameter = 4.2
set_screw_head_diameter = 8.0
set_screw_head_depth = 4.0
set_screw_offset = boss_diameter / 4.0
fillet_radius = 2.0
slot_width = 6.0
slot_length = 30.0
slot_depth = 8.0

result = Box(block_length, block_width, block_thickness)
result = result - Cylinder(through_hole_diameter / 2, block_thickness + 2)
result = result + Pos(0, 0, block_thickness / 2 + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
result = result - Pos(set_screw_offset, 0, block_thickness / 2 + boss_height / 2) * Cylinder(set_screw_diameter / 2, boss_height + block_thickness + 2)
result = result - Pos(set_screw_offset, 0, block_thickness / 2 + boss_height - set_screw_head_depth / 2) * Cylinder(set_screw_head_diameter / 2, set_screw_head_depth)
result = result - Pos(0, 0, block_thickness / 2 + boss_height - slot_depth / 2) * Box(slot_length, slot_width, slot_depth)
top_edges = result.edges().sort_by(Axis.Z)[-1:]
result = fillet(top_edges, fillet_radius)

part = result
part.name = "block_with_boss_and_holes"
export_step(part, "output.step")
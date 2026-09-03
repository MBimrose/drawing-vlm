from build123d import *

block_length = 80.0
block_width = 50.0
block_thickness = 10.0
boss_diameter = 30.0
boss_height = 20.0
central_hole_diameter = 12.0
set_screw_hole_diameter = 4.2
set_screw_offset = boss_diameter / 4.0
slot_width = 6.0
slot_length = 30.0
slot_depth = 8.0
chamfer_size = 1.0

result = Box(block_length, block_width, block_thickness)
result = result + Pos(0, 0, block_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result - Cylinder(central_hole_diameter/2, block_thickness + boss_height + 2)
result = result - Pos(set_screw_offset, 0, 0) * Cylinder(set_screw_hole_diameter/2, block_thickness + boss_height + 2)
result = result - Pos(0, 0, block_thickness/2 + boss_height - slot_depth/2) * Box(slot_length, slot_width, slot_depth)
top_edges = result.edges().sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "block_with_boss_and_holes"
export_step(part, "output.step")
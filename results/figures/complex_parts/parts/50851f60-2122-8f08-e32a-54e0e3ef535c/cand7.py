from build123d import *

outer_diameter = 60.0
inner_diameter = 30.0
height = 20.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
groove_width = 5.0
groove_depth = 2.0
slot_width = 4.0
slot_depth = 12.0
slot_count = 4
chamfer_size = 1.0
pocket_width = 8.0
pocket_depth = 4.0

import math

result = Cylinder(outer_diameter / 2.0, height) - Cylinder(inner_diameter / 2.0, height)

groove = Pos(0, 0, height - groove_depth / 2.0) * Cylinder((outer_diameter / 2.0) - groove_width, groove_depth)
result = result - groove

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_diameter / 2.0 - slot_width / 2.0, 0, 0) * Box(slot_width, slot_width, slot_depth)
    result = result - slot

pocket = Pos(inner_diameter / 2.0 - pocket_depth / 2.0, 0, height / 2.0) * Box(pocket_depth, pocket_width, pocket_width)
result = result - pocket

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "hollow_cylinder_with_groove_slots_pocket"
export_step(part, "output.step")
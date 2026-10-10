from build123d import *
import math

outer_diameter = 60.0
thickness = 10.0
central_hole_diameter = 10.0
boss_diameter = 15.0
boss_height = 5.0
slot_width = 2.0
slot_depth = 4.0
slot_count = 12
chamfer_size = 0.5

result = Cylinder(outer_diameter / 2, thickness)
result = result - Cylinder(central_hole_diameter / 2, thickness)
result = result + Pos(0, 0, thickness / 2 + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(boss_diameter / 2 - slot_depth / 2, 0, thickness / 2 + boss_height / 2) * Box(slot_width, slot_depth, boss_height)
    result = result - slot

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "flanged_disc_with_slots"
export_step(part, "output.step")
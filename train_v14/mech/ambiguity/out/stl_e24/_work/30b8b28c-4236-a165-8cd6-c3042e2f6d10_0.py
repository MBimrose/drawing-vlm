from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 28.0
thickness = 1.5
slot_width = 1.5
slot_length = 5.0
slot_count = 8
chamfer_size = 0.3
boss_diameter = 10.0
boss_height = 0.5
boss_offset = 20.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
slot_radius = outer_radius - slot_length / 2.0

result = Cylinder(outer_radius, thickness) - Cylinder(inner_radius, thickness)
result = chamfer(result.edges(), chamfer_size)

for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    slot = Pos(px, py, 0) * Rot(0, 0, math.degrees(angle)) * Box(slot_length, slot_width, thickness)
    result = result - slot

boss = Pos(boss_offset, 0, 0) * Cylinder(boss_diameter / 2.0, boss_height)
result = result + boss

part = result
part.name = "ring_with_slots_and_boss"
export_step(part, "output.step")
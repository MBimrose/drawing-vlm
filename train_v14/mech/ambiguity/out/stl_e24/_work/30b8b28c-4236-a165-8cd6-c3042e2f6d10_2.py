from build123d import *
import math

outer_radius = 30.0
inner_radius = 14.0
thickness = 1.5
slot_width = 1.5
slot_count = 8
chamfer_size = 0.3
boss_radius = 6.0
boss_height = 0.5
boss_offset = 20.0

ring = Cylinder(outer_radius, thickness) - Cylinder(inner_radius, thickness)
ring = chamfer(ring.edges(), chamfer_size)

slot_length = outer_radius - inner_radius
slot_center_x = inner_radius + slot_length / 2
slot_box = Box(slot_width, slot_length, thickness)

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    ring = ring - Pos(slot_center_x, 0, 0) * Rot(0, 0, angle) * slot_box

boss = Pos(boss_offset, 0, 0) * Cylinder(boss_radius, boss_height)
part = ring + boss
part.name = "ring_with_slots_and_boss"
export_step(part, "output.step")
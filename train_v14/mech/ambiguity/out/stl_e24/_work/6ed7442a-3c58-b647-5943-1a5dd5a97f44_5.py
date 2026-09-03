from build123d import *
import math

outer_diameter = 80.0
thickness = 5.0
boss_diameter = 12.0
boss_height = 2.0
slot_width = 5.0
slot_length = 30.0
slot_count = 6
slot_chamfer = 0.5
slot_offset = outer_diameter/2 - slot_length/2 - 2.0

base = Pos(0, 0, thickness/2) * Cylinder(outer_diameter/2, thickness)
boss = Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

slot_body = Pos(slot_offset, 0, thickness/2) * Box(slot_length, slot_width, thickness)
slot_edges = slot_body.edges().filter_by(Axis.Z)
slot_body = chamfer(slot_edges, slot_chamfer)

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    rotated_slot = Rot(0, 0, angle) * slot_body
    result = result - rotated_slot

part = result
part.name = "disc_with_slots"
export_step(part, "output.step")
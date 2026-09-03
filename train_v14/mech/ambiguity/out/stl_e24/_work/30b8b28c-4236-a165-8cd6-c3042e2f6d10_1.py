from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 28.0
thickness = 1.5
slot_width = 1.5
slot_length = 5.0
num_slots = 8
chamfer_size = 0.2
boss_diameter = 10.0
boss_height = 0.8

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
slot_center_radius = outer_radius - slot_length / 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, thickness / 2) * Cylinder(inner_radius, thickness)
solid_body = chamfer(solid_body.edges(), chamfer_size)

for i in range(num_slots):
    angle = math.radians(i * 360.0 / num_slots)
    px = slot_center_radius * math.cos(angle)
    py = slot_center_radius * math.sin(angle)
    slot = Pos(px, py, thickness / 2) * Rot(0, 0, math.degrees(angle)) * Box(slot_length, slot_width, thickness)
    solid_body = solid_body - slot

boss = Pos(0, 0, thickness - boss_height / 2) * Cylinder(boss_diameter / 2.0, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "washer_with_slots_and_boss"
export_step(part, "output.step")
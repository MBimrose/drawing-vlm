from build123d import *
import math

outer_diameter = 80.0
thickness = 5.0
slot_width = 5.0
slot_length = 30.0
slot_count = 6
slot_angle = 360.0 / slot_count
hex_flat_distance = 12.0
hex_depth = 2.0
chamfer_size = 0.5
boss_diameter = 10.0
boss_height = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=thickness)

solid_body = p.part

for i in range(slot_count):
    angle = i * slot_angle
    slot = Rot(0, 0, angle) * Pos(outer_diameter / 2 - slot_length / 2, 0, thickness / 2) * Box(slot_length, slot_width, thickness)
    solid_body = solid_body - slot

with BuildPart() as hp:
    with BuildSketch() as hs:
        RegularPolygon(hex_flat_distance, 6)
    extrude(amount=hex_depth)
hex_prism = Pos(0, 0, thickness - hex_depth) * hp.part
solid_body = solid_body - hex_prism

boss = Pos(0, 0, boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "slotted_disc_with_hex_recess"
export_step(part, "output.step")
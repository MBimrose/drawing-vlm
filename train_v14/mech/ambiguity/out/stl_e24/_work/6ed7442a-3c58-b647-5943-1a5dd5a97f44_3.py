from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 5.0
slot_width = 5.0
slot_length = (outer_diameter - inner_diameter) / 2.0
slot_count = 6
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2.0)
    extrude(amount=thickness)

solid_body = p.part

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(inner_diameter / 2.0 + slot_length / 2.0, 0, thickness / 2.0) * Box(slot_length, slot_width, thickness)
    solid_body = solid_body - slot

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "slotted_disk"
export_step(part, "output.step")
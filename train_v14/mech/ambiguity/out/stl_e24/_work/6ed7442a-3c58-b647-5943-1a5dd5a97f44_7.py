from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 10.0
thickness = 5.0
slot_width = 5.0
slot_length = 30.0
slot_count = 6
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_diameter / 2 - slot_length / 2, 0, thickness / 2) * Box(slot_length, slot_width, thickness)
    solid_body = solid_body - slot

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "slotted_disc"
export_step(part, "output.step")
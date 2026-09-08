from build123d import *

outer_diameter = 80.0
thickness = 7.3
slot_length = 50.0
slot_width = 7.3
slot_depth = 3.6

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=thickness)

solid_body = p.part

with BuildPart() as slot_p:
    with BuildSketch() as slot_s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=slot_depth)

slot_solid = Pos(0, 0, thickness - slot_depth) * slot_p.part
solid_body = solid_body - slot_solid

part = solid_body
part.name = "cylinder_with_slot"
export_step(part, "output.step")
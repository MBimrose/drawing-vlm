from build123d import *

leg_width = 12.0
vertical_height = 80.0
horizontal_length = 60.0
thickness = 8.0
slot_width = 6.0
slot_length = 30.0
slot_depth = thickness - 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_width, 0), (leg_width, vertical_height - leg_width),
                     (horizontal_length, vertical_height - leg_width),
                     (horizontal_length, vertical_height), (0, vertical_height), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
slot_box = Box(slot_width, slot_depth, slot_length)
slot_box = Pos(horizontal_length/2, vertical_height - slot_depth/2, thickness/2) * slot_box
solid_body = solid_body - slot_box

part = solid_body
part.name = "L_bracket_with_slot"
export_step(part, "output.step")
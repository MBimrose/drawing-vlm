from build123d import *

vertical_leg_length = 80.0
horizontal_leg_length = 60.0
leg_width = 12.0
thickness = 8.0
slot_width = 6.0
slot_length = 30.0
slot_depth = thickness - 1.0
hole_diameter = 5.0
hole_offset = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_width, 0), (leg_width, vertical_leg_length - leg_width),
                     (horizontal_leg_length, vertical_leg_length - leg_width),
                     (horizontal_leg_length, vertical_leg_length), (0, vertical_leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

slot_box = Pos(horizontal_leg_length / 2, vertical_leg_length - leg_width / 2, thickness - slot_depth / 2) * Box(slot_width, slot_length, slot_depth)
solid_body = solid_body - slot_box

hole_cyl = Pos(leg_width / 2, hole_offset, thickness / 2) * Cylinder(hole_diameter / 2, thickness)
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "L_Bracket"
export_step(part, "output.step")
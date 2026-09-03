from build123d import *

horizontal_length = 80.0
vertical_length = 60.0
leg_width = 12.0
thickness = 10.0
slot_width = 6.0
slot_depth = 4.0
slot_offset = 30.0
hole_diameter = 5.0
hole_offset1 = 15.0
hole_offset2 = 45.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0,0), (horizontal_length,0), (horizontal_length,leg_width),
                     (leg_width,leg_width), (leg_width,vertical_length),
                     (0,vertical_length), close=True)
        make_face()
    extrude(amount=thickness)

solid = p.part

slot_box = Pos(slot_depth/2, slot_offset, thickness/2) * Box(slot_depth, slot_width, slot_width)
solid = solid - slot_box

for y_pos in [hole_offset1, hole_offset2]:
    hole = Pos(0, y_pos, thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, thickness)
    solid = solid - hole

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")
from build123d import *

leg_thickness = 8.0
vertical_leg_length = 70.0
horizontal_leg_length = 60.0
bracket_width = 20.0
rib_thickness = 4.0
rib_height = 10.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as s1:
        with BuildLine() as l1:
            Polyline((0,0), (0, vertical_leg_length), (leg_thickness, vertical_leg_length),
                     (leg_thickness, leg_thickness), (horizontal_leg_length, leg_thickness),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=bracket_width)
    with BuildSketch() as s2:
        with BuildLine() as l2:
            Polyline((0, vertical_leg_length), (rib_height, vertical_leg_length),
                     (0, vertical_leg_length - rib_height), close=True)
        make_face()
    extrude(amount=bracket_width)

solid = p.part
hole_r = hole_diameter / 2
hole_tool = Rot(90, 0, 0) * Cylinder(hole_r, vertical_leg_length + 20)
for x in [hole_offset, hole_offset + hole_spacing]:
    solid = solid - Pos(x, vertical_leg_length/2, bracket_width/2) * hole_tool

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")
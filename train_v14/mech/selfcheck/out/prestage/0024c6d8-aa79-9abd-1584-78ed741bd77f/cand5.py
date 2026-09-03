from build123d import *

leg_width = 20.0
vertical_leg_length = 80.0
horizontal_leg_length = 70.0
thickness = 10.0
notch_width = 4.0
notch_length = 20.0
hole_diameter = 5.0
hole_depth = 8.0
hole_spacing = 12.0
hole_offset_from_inner = 10.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (0, vertical_leg_length), (leg_width, vertical_leg_length),
                     (leg_width, leg_width), (horizontal_leg_length, leg_width),
                     (horizontal_leg_length, 0), close=True)
        make_face()
    extrude(amount=thickness)

solid = p.part

notch = Pos(leg_width/2, vertical_leg_length/2, thickness/2) * Box(notch_width, notch_length, thickness)
solid = solid - notch

for i in range(4):
    hx = leg_width + hole_offset_from_inner + i * hole_spacing
    hy = leg_width / 2
    hole = Pos(hx, hy, thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid = solid - hole

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

part = solid
part.name = "L_Bracket"
export_step(part, "output.step")
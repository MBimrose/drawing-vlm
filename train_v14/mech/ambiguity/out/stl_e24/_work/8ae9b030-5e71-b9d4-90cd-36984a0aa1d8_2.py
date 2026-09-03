from build123d import *

leg_long = 80.0
leg_short = 60.0
thickness = 8.0
bracket_depth = 10.0
pocket_width = 6.0
pocket_depth = 30.0
hole_diameter = 6.0
hole_spacing = 20.0
hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_long, 0))
            l2 = Line(l1 @ 1, (leg_long, thickness))
            l3 = Line(l2 @ 1, (thickness, thickness))
            l4 = Line(l3 @ 1, (thickness, leg_short))
            l5 = Line(l4 @ 1, (0, leg_short))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=bracket_depth)

solid_body = p.part

pocket = Pos(thickness/2, leg_short/2, bracket_depth/2) * Box(pocket_depth, pocket_width, thickness)
solid_body = solid_body - pocket

for i in range(3):
    x = hole_offset + i * hole_spacing
    hole = Pos(x, leg_short/2, bracket_depth/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, leg_short + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")
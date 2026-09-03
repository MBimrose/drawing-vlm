from build123d import *

leg_length_long = 80.0
leg_length_short = 60.0
leg_width = 10.0
leg_thickness = 8.0
notch_width = 10.0
notch_depth = 6.0
hole_diameter = 6.0
hole_depth = 5.0
fillet_radius = 1.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_length_long, 0))
            l2 = Line(l1 @ 1, (leg_length_long, leg_width))
            l3 = Line(l2 @ 1, (leg_width + leg_thickness, leg_width))
            l4 = Line(l3 @ 1, (leg_width + leg_thickness, leg_length_short + leg_width))
            l5 = Line(l4 @ 1, (0, leg_length_short + leg_width))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=leg_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

notch = Pos(leg_thickness/2, leg_length_short/2, leg_thickness/2) * Box(notch_width, notch_depth, leg_thickness)
solid_body = solid_body - notch

for y_pos in [leg_width/2, leg_width/2 + 5]:
    hole = Pos(leg_length_long - hole_depth/2, y_pos, leg_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")
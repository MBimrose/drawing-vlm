from build123d import *

leg_length = 80.0
leg_width = 30.0
thickness = 15.0
wall_thickness = 4.0
notch_radius = 10.0
fillet_radius = 4.0
hole_diameter = 8.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_width + wall_thickness, 0))
            l2 = Line(l1 @ 1, (leg_width + wall_thickness, leg_width))
            l3 = Line(l2 @ 1, (leg_width, leg_width))
            l4 = Line(l3 @ 1, (leg_width, leg_length))
            l5 = Line(l4 @ 1, (0, leg_length))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

notch = Pos(leg_width / 2, leg_length, thickness / 2) * Cylinder(notch_radius, thickness)
solid_body = solid_body - notch

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

vert_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vert_edges, fillet_radius)

hole = Pos(leg_width / 2, leg_length, thickness / 2) * Cylinder(hole_diameter / 2, thickness)
solid_body = solid_body - hole

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")
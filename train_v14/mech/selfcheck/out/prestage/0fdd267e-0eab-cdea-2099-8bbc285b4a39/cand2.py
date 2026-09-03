from build123d import *

leg_length_long = 80.0
leg_length_short = 50.0
leg_width = 15.0
thickness = 8.0
inner_fillet_radius = 6.0
hole_diameter = 5.0
countersink_diameter = 9.0
countersink_angle = 82.0
hole_offset = 12.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (leg_length_short, 0))
            l2 = Line(l1 @ 1, (leg_length_short, leg_width))
            l3 = Line(l2 @ 1, (leg_length_short + leg_length_long, leg_width))
            l4 = Line(l3 @ 1, (leg_length_short + leg_length_long, 0))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    extrude(amount=thickness)

solid_body = p.part

inner_edges = [e for e in solid_body.edges() if abs(e.center().X - leg_length_short) < 0.1 and abs(e.center().Y - leg_width) < 0.1]
solid_body = fillet(inner_edges, inner_fillet_radius)

hole_x = leg_length_short + leg_length_long - hole_offset
hole_y = leg_width / 2
solid_body = solid_body - Pos(hole_x, hole_y, thickness) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, thickness, countersink_angle)

solid_body = chamfer(solid_body.edges(), chamfer_distance)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")
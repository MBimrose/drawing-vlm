from build123d import *

leg_length_long = 80.0
leg_length_short = 50.0
leg_width = 20.0
thickness = 8.0
fillet_radius = 4.0
pocket_length = 30.0
pocket_width = 12.0
pocket_depth = 4.0
hole_diameter = 6.0
countersink_diameter = 10.0
countersink_angle = 82.0
rib_height = 6.0
rib_width = 4.0
rib_spacing = 10.0
rib_count = 3

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length_long, 0), (leg_length_long, leg_length_short),
                     (leg_length_long - thickness, leg_length_short),
                     (leg_length_long - thickness, leg_length_short + leg_width),
                     (leg_length_long - 2 * thickness, leg_length_short + leg_width),
                     (leg_length_long - 2 * thickness, leg_width),
                     (0, leg_width), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

z_edges = solid_body.edges().filter_by(Axis.Z)
max_x_edges = z_edges.sort_by(Axis.X)[-2:]
solid_body = fillet(max_x_edges, fillet_radius)

pocket = Pos(leg_length_long / 2, leg_width / 2, pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole_x = leg_length_long - thickness / 2
hole_y = leg_length_short + leg_width / 2
csk_hole = Pos(hole_x, hole_y, thickness) * CounterSinkHole(hole_diameter / 2, countersink_diameter / 2, thickness, countersink_angle)
solid_body = solid_body - csk_hole

for i in range(rib_count):
    rib_x = leg_length_long / 2 - rib_spacing * (rib_count - 1) / 2 + i * rib_spacing
    rib = Pos(rib_x, 0, rib_height / 2) * Box(rib_width, leg_width, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "L_bracket_with_pocket_hole_ribs"
export_step(part, "output.step")
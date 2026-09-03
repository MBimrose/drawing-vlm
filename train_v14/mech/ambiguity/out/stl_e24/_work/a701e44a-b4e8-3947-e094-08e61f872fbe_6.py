from build123d import *

leg_length = 70.0
leg_width = 20.0
thickness = 8.0
rib_width = 6.0
rib_height = 12.0
rib_spacing = 5.0
rib_count = 3
hole_diameter = 5.0
hole_offset = 15.0
fillet_radius = 4.0
pocket_depth = 2.0
pocket_width = 12.0
pocket_length = 30.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_length - leg_width, leg_width),
                     (leg_length - leg_width, leg_length),
                     (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

for i in range(rib_count):
    x = leg_width + rib_spacing + i * (rib_width + rib_spacing)
    y = leg_width / 2
    solid_body = solid_body + Pos(x, y, thickness / 4) * Box(rib_width, rib_height, thickness / 2)

solid_body = solid_body - Pos(leg_length - leg_width / 2, leg_length - hole_offset, thickness / 2) * Cylinder(hole_diameter / 2, thickness)

solid_body = solid_body - Pos(leg_length / 2, leg_width / 2, thickness - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
max_x_edges = vertical_edges.sort_by(Axis.X)[-2:]
solid_body = fillet(max_x_edges, fillet_radius)

part = solid_body
part.name = "L_bracket_with_ribs"
export_step(part, "output.step")
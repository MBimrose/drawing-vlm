from build123d import *

leg_length = 70.0
leg_width = 20.0
thickness = 10.0
pocket_radius = 15.0
pocket_depth = thickness - 1.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length),
                     (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body - Pos(leg_width, leg_width, thickness - pocket_depth / 2) * Cylinder(pocket_radius, pocket_depth)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "L_bracket_with_pocket"
export_step(part, "output.step")
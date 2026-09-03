from build123d import *

block_length = 80.0
block_width = 25.0
block_thickness = 5.0
arc_radius = 30.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (block_length, 0))
            l2 = Line(l1 @ 1, (block_length, block_width))
            l3 = Line(l2 @ 1, (0, block_width))
            RadiusArc(l3 @ 1, (0, 0), arc_radius)
        make_face()
    extrude(amount=block_thickness)

solid_body = p.part
x_face = solid_body.faces().sort_by(Axis.X)[-1]
x_edges = x_face.edges()
solid_body = chamfer(x_edges, chamfer_distance)

part = solid_body
part.name = "arc_block"
export_step(part, "output.step")
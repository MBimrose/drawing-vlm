from build123d import *

clip_length = 80.0
clip_width = 25.0
clip_thickness = 5.0
arc_radius = 12.0
chamfer_dist = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (clip_length, 0))
            l2 = Line(l1 @ 1, (clip_length, clip_width))
            l3 = Line(l2 @ 1, (0, clip_width))
            RadiusArc(l3 @ 1, (0, 0), arc_radius)
        make_face()
    extrude(amount=clip_thickness)

solid_body = p.part
x_face = solid_body.faces().sort_by(Axis.X)[-1]
x_edges = x_face.edges()
solid_body = chamfer(x_edges, chamfer_dist)

part = solid_body
part.name = "clip"
export_step(part, "output.step")
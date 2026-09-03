from build123d import *

beam_length = 80.0
flange_width = 50.0
flange_thickness = 12.0
web_height = 30.0
web_thickness = 10.0
chamfer_size = 1.0

pts = [
    (0, 0),
    (web_thickness/2, 0),
    (web_thickness/2, web_height),
    (flange_width/2, web_height),
    (flange_width/2, web_height + flange_thickness),
    (0, web_height + flange_thickness)
]

full_pts = pts + [(-x, y) for x, y in reversed(pts[1:-1])]

with BuildPart() as p:
    with BuildSketch() as s:
        Polygon(*full_pts)
    extrude(amount=beam_length)

solid_body = p.part
z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges, chamfer_size)

part = solid_body
part.name = "I-beam"
export_step(part, "output.step")
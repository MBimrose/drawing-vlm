from build123d import *

beam_length = 80.0
beam_height = 40.0
flange_width = 50.0
flange_thickness = 12.0
web_thickness = 10.0
chamfer_size = 1.0
hole_diameter = 6.0

pts = [
    (0, 0),
    (web_thickness/2, 0),
    (web_thickness/2, beam_height - flange_thickness),
    (flange_width/2, beam_height - flange_thickness),
    (flange_width/2, beam_height),
    (0, beam_height)
]

full_pts = pts + [(-x, y) for x, y in reversed(pts[1:-1])]

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(*full_pts, close=True)
        make_face()
    extrude(amount=beam_length)

solid_body = p.part
z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges, chamfer_size)
solid_body = solid_body - Pos(0, 0, beam_length/2) * Cylinder(hole_diameter/2, beam_length + 10)

part = solid_body
part.name = "I-beam"
export_step(part, "output.step")
from build123d import *

beam_length = 80.0
overall_height = 60.0
flange_width = 40.0
flange_thickness = 5.0
web_thickness = 5.0
shell_thickness = 2.0

pts = [
    (0, -overall_height/2),
    (flange_width/2, -overall_height/2),
    (flange_width/2, -overall_height/2 + flange_thickness),
    (web_thickness/2, -overall_height/2 + flange_thickness),
    (web_thickness/2, overall_height/2 - flange_thickness),
    (flange_width/2, overall_height/2 - flange_thickness),
    (flange_width/2, overall_height/2),
    (0, overall_height/2)
]

full_pts = pts + [(-x, z) for x, z in reversed(pts[1:-1])]

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline(*full_pts, close=True)
        make_face()
    extrude(amount=beam_length)

solid_body = p.part
solid_body = offset(solid_body, amount=-shell_thickness)

part = solid_body
part.name = "I-beam"
export_step(part, "output.step")
from build123d import *

beam_length = 80.0
beam_height = 60.0
flange_width = 40.0
flange_thickness = 5.0
web_thickness = 5.0
shell_thickness = 2.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 0.5

pts = [
    (0, -beam_height/2),
    (flange_width/2, -beam_height/2),
    (flange_width/2, -beam_height/2 + flange_thickness),
    (web_thickness/2, -beam_height/2 + flange_thickness),
    (web_thickness/2, beam_height/2 - flange_thickness),
    (flange_width/2, beam_height/2 - flange_thickness),
    (flange_width/2, beam_height/2),
    (0, beam_height/2)
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

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
pocket = Pos(0, beam_length/2, top_face.center().Z - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "I-beam_with_pocket"
export_step(part, "output.step")
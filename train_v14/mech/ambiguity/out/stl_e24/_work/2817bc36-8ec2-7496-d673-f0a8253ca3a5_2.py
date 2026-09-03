from build123d import *

beam_length = 80.0
beam_height = 60.0
flange_width = 40.0
flange_thickness = 5.0
web_thickness = 4.0
hole_diameter = 6.0
chamfer_size = 0.5

half_flange = flange_width / 2.0
half_web = web_thickness / 2.0
half_height = beam_height / 2.0

pts = [
    (0, -half_height),
    (half_web, -half_height),
    (half_web, -half_flange),
    (half_flange, -half_flange),
    (half_flange, -half_flange + flange_thickness),
    (half_web, -half_flange + flange_thickness),
    (half_web, half_flange - flange_thickness),
    (half_flange, half_flange - flange_thickness),
    (half_flange, half_flange),
    (half_web, half_flange),
    (half_web, half_height),
    (0, half_height),
    (-half_web, half_height),
    (-half_web, half_flange),
    (-half_flange, half_flange),
    (-half_flange, half_flange - flange_thickness),
    (-half_web, half_flange - flange_thickness),
    (-half_web, -half_flange + flange_thickness),
    (-half_flange, -half_flange + flange_thickness),
    (-half_flange, -half_flange),
    (-half_web, -half_flange),
    (-half_web, -half_height),
]

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(*pts, close=True)
        make_face()
    extrude(amount=beam_length)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, beam_length/2) * Cylinder(hole_diameter/2, beam_length)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "I-beam"
export_step(part, "output.step")
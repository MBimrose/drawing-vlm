from build123d import *

beam_length = 80.0
overall_height = 60.0
flange_width = 40.0
web_thickness = 4.0
flange_thickness = 5.0
hole_diameter = 6.0
chamfer_size = 0.5

half_flange = flange_width / 2.0
half_web = web_thickness / 2.0
half_height = overall_height / 2.0

pts = [
    (-half_flange, -flange_thickness/2.0),
    (-half_web, -flange_thickness/2.0),
    (-half_web, -half_height),
    ( half_web, -half_height),
    ( half_web, -flange_thickness/2.0),
    ( half_flange, -flange_thickness/2.0),
    ( half_flange,  flange_thickness/2.0),
    ( half_web,  flange_thickness/2.0),
    ( half_web,  half_height),
    (-half_web,  half_height),
    (-half_web,  flange_thickness/2.0),
    (-half_flange,  flange_thickness/2.0),
]

with BuildPart() as p:
    with BuildSketch() as s:
        Polygon(*pts)
    extrude(amount=beam_length)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, beam_length/2) * Cylinder(hole_diameter/2, beam_length)
z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges, chamfer_size)

part = solid_body
part.name = "I-beam"
export_step(part, "output.step")
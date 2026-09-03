from build123d import *

beam_length = 80.0
beam_height = 60.0
flange_width = 40.0
flange_thickness = 5.0
web_thickness = 4.0
hole_diameter = 6.0
chamfer_size = 0.5

pts = [
    (0, -beam_height/2),
    (web_thickness/2, -beam_height/2),
    (web_thickness/2, -flange_thickness/2),
    (flange_width/2, -flange_thickness/2),
    (flange_width/2, flange_thickness/2),
    (web_thickness/2, flange_thickness/2),
    (web_thickness/2, beam_height/2),
    (0, beam_height/2)
]

full_pts = pts + [(-x, y) for x, y in reversed(pts[1:-1])]

with BuildPart() as p:
    with BuildSketch() as s:
        Polygon(*full_pts)
    extrude(amount=beam_length)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, beam_length/2) * Cylinder(hole_diameter/2, beam_length)
z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges, chamfer_size)

part = solid_body
part.name = "I_beam"
export_step(part, "output.step")
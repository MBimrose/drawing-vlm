from build123d import *

overall_width = 80.0
overall_height = 30.0
flange_thickness = 5.0
web_thickness = 6.0
wall_thickness = 0.8
chamfer_size = 1.0
hole_diameter = 18.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-overall_width/2, overall_height/2),
                (overall_width/2, overall_height/2),
                (overall_width/2, overall_height/2 - flange_thickness),
                (web_thickness/2, overall_height/2 - flange_thickness),
                (web_thickness/2, -overall_height/2),
                (-web_thickness/2, -overall_height/2),
                (-web_thickness/2, overall_height/2 - flange_thickness),
                (-overall_width/2, overall_height/2 - flange_thickness),
                close=True
            )
        make_face()
    extrude(amount=overall_height)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness)

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:]
solid_body = chamfer(top_edges, chamfer_size)

solid_body = solid_body - Cylinder(hole_diameter/2, overall_height * 2)

part = solid_body
part.name = "T_channel"
export_step(part, "output.step")
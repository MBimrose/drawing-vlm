from build123d import *

flange_width = 80.0
flange_thickness = 5.0
web_height = 30.0
web_width = 25.0
extrude_depth = 30.0
hole_diameter = 18.5
fillet_radius = 3.9

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-flange_width/2, 0),
                (flange_width/2, 0),
                (flange_width/2, -flange_thickness),
                (web_width/2, -flange_thickness),
                (web_width/2, -web_height),
                (-web_width/2, -web_height),
                (-web_width/2, -flange_thickness),
                (-flange_width/2, -flange_thickness),
                close=True
            )
        make_face()
    extrude(amount=extrude_depth)

solid_body = p.part
hole_center_y = -web_height/2
solid_body = solid_body - Pos(0, hole_center_y, extrude_depth/2) * Cylinder(hole_diameter/2, extrude_depth)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
inner_edges = [e for e in vertical_edges if abs(e.center().X) < web_width/2 + 0.1]
solid_body = fillet(inner_edges, fillet_radius)

part = solid_body
part.name = "T_profile_with_hole"
export_step(part, "output.step")
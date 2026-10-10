from build123d import *

leg_length = 80.0
leg_width = 30.0
thickness = 15.0
wall_thickness = 4.0
hole_diameter = 20.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_width + thickness, 0), (leg_width + thickness, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length), (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

hole = Pos(leg_width/2, leg_length, thickness/2) * Cylinder(hole_diameter/2, thickness + 2)
solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")
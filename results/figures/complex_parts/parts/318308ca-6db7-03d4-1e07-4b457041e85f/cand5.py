from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 15.0
wall_thickness = 4.0
tab_width = 10.0
tab_length = 30.0
hole_diameter = 12.0
countersink_diameter = 20.0
countersink_angle = 90.0
fillet_radius = 3.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-bracket_width/2, -bracket_length/2),
                (bracket_width/2, -bracket_length/2),
                (bracket_width/2, bracket_length/2 - tab_length),
                (bracket_width/2 - tab_width, bracket_length/2 - tab_length),
                (bracket_width/2 - tab_width, bracket_length/2),
                (-bracket_width/2, bracket_length/2),
                close=True
            )
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

hole = CounterSinkHole(hole_diameter/2, countersink_diameter/2, bracket_thickness, countersink_angle)
solid_body = solid_body - Pos(0, bracket_length/2, bracket_thickness/2) * hole

z_edges = solid_body.edges().filter_by(Axis.Z)
tab_edges = [e for e in z_edges if e.center().X > 0 and e.center().Y > 0]
solid_body = fillet(tab_edges, fillet_radius)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")
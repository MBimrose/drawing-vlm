from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 15.0
wall_thickness = 4.0
notch_width = 12.0
notch_depth = 30.0
hole_diameter = 8.0
countersink_diameter = 14.0
countersink_angle = 82.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-bracket_width/2, -bracket_length/2),
                (bracket_width/2, -bracket_length/2),
                (bracket_width/2, -bracket_length/2 + notch_depth),
                (bracket_width/2 - notch_width, -bracket_length/2 + notch_depth),
                (bracket_width/2 - notch_width, bracket_length/2),
                (-bracket_width/2, bracket_length/2),
                close=True
            )
        make_face()
    extrude(amount=bracket_thickness)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

csk_hole = CounterSinkHole(hole_diameter/2, countersink_diameter/2, bracket_thickness, countersink_angle)
solid_body = solid_body - Pos(0, bracket_length/2, bracket_thickness/2) * csk_hole

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")
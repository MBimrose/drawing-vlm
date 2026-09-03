from build123d import *

overall_length = 80.0
overall_width = 40.0
overall_thickness = 15.0
wall_thickness = 4.0
step_height = 30.0
step_width = 30.0
hole_diameter = 12.0
countersink_diameter = 20.0
countersink_angle = 90.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (overall_width, 0), (overall_width, step_height),
                     (step_width, step_height), (step_width, overall_length),
                     (0, overall_length), close=True)
        make_face()
    extrude(amount=overall_thickness)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

hole_x = step_width / 2
hole_y = overall_length
hole = CounterSinkHole(hole_diameter/2, countersink_diameter/2, overall_thickness, countersink_angle)
solid_body = solid_body - Pos(hole_x, hole_y, overall_thickness/2) * hole

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "stepped_shelled_block"
export_step(part, "output.step")
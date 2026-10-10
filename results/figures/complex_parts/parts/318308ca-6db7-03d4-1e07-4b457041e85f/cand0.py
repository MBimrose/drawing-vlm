from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 15.0
wall_thickness = 4.0
step_width = 10.0
step_length = 30.0
fillet_radius = 2.0
countersink_diameter = 12.0
countersink_angle = 90.0
countersink_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-channel_width/2, -channel_length/2),
                (channel_width/2, -channel_length/2),
                (channel_width/2, channel_length/2 - step_length),
                (channel_width/2 - step_width, channel_length/2 - step_length),
                (channel_width/2 - step_width, channel_length/2),
                (-channel_width/2, channel_length/2),
                close=True
            )
        make_face()
    extrude(amount=channel_height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

csk = CounterSinkHole(countersink_diameter/2, countersink_diameter, countersink_angle)
solid_body = solid_body - Pos(0, channel_length/2, channel_height/2) * csk

part = solid_body
part.name = "stepped_channel"
export_step(part, "output.step")
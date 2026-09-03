from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.0
groove_depth = 8.0
groove_width = 15.0
chamfer_size = 0.5
hole_diameter = 5.0
hole_spacing = 20.0

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

with BuildPart() as gp:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            l1 = Line((-groove_width/2, 0), (0, groove_depth))
            l2 = Line(l1@1, (groove_width/2, 0))
            l3 = Line(l2@1, (-groove_width/2, 0))
        make_face()
    extrude(amount=channel_length)
groove = gp.part
base = base - groove

hole1 = Pos(-hole_spacing/2, channel_width/2, channel_height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, channel_width + 10)
hole2 = Pos(hole_spacing/2, channel_width/2, channel_height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, channel_width + 10)
base = base - hole1 - hole2

vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_size)

part = base
part.name = "channel_with_groove"
export_step(part, "output.step")
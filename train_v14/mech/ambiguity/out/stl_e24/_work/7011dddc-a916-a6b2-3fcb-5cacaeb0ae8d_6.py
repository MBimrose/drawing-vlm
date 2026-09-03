from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.0
groove_width = 16.0
groove_depth = 8.0
fillet_radius = 0.5
chamfer_distance = 0.5
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

z_edges = base.edges().filter_by(Axis.Z)
base = chamfer(z_edges.sort_by(Axis.X)[-2:], chamfer_distance)
base = chamfer(z_edges.sort_by(Axis.X)[:2], chamfer_distance)

z_edges = base.edges().filter_by(Axis.Z)
base = fillet(z_edges.sort_by(Axis.Y)[-2:], fillet_radius)
base = fillet(z_edges.sort_by(Axis.Y)[:2], fillet_radius)

for x in [-hole_spacing/2, hole_spacing/2]:
    base = base - Pos(x, channel_width/2, channel_height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, channel_width + 10)

part = base
part.name = "channel_with_groove"
export_step(part, "output.step")
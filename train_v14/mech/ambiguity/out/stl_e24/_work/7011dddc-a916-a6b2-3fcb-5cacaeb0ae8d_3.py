from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.0
v_groove_depth = 6.0
v_groove_width = 12.0
fillet_radius = 0.5
hole_diameter = 5.0
hole_spacing = 20.0

base = Pos(0, 0, channel_height / 2) * Box(channel_length, channel_width, channel_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

with BuildPart() as gp:
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine() as bl:
            l1 = Line((-v_groove_width / 2, 0), (0, v_groove_depth))
            l2 = Line(l1 @ 1, (v_groove_width / 2, 0))
            l3 = Line(l2 @ 1, (-v_groove_width / 2, 0))
        make_face()
    extrude(amount=channel_length)
groove = Pos(-channel_length / 2, 0, 0) * gp.part

result = base - groove
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

for x in [-hole_spacing / 2, hole_spacing / 2]:
    hole = Pos(x, channel_width / 2, channel_height / 2) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, channel_width)
    result = result - hole

part = result
part.name = "channel_with_v_groove"
export_step(part, "output.step")
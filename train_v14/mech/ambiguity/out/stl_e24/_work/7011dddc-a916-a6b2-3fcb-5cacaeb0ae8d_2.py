from build123d import *

chute_length = 80.0
chute_width = 40.0
chute_height = 30.0
wall_thickness = 2.0
channel_depth = 8.0
channel_top_width = 30.0
channel_bottom_width = 10.0
fillet_radius = 0.5
mount_hole_dia = 5.0
mount_hole_spacing = 20.0

outer = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)
inner = Pos(0, 0, wall_thickness + (chute_height - wall_thickness)/2) * Box(chute_length - 2*wall_thickness, chute_width - 2*wall_thickness, chute_height - wall_thickness)
base = outer - inner

with BuildPart() as vp:
    with BuildSketch(Plane.YZ) as vs:
        with BuildLine() as vl:
            Polyline((-channel_bottom_width/2, 0), (channel_bottom_width/2, 0), (0, channel_depth), close=True)
        make_face()
    extrude(amount=chute_length)
v_channel = vp.part

result = base - v_channel
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, chute_width/2, chute_height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_dia/2, chute_width)
    result = result - hole

part = result
part.name = "chute"
export_step(part, "output.step")
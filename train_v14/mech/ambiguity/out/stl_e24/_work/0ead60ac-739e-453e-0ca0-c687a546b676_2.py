from build123d import *
import math

bar_length = 80.0
bar_width = 20.0
bar_height = 10.0
v_groove_depth = 3.0
v_groove_angle = 60.0
hole_diameter = 4.0
hole_spacing = 30.0
rib_height = 2.0
rib_width = 4.0
rib_spacing = 15.0
chamfer_size = 0.5

v_groove_half_width = v_groove_depth * math.tan(math.radians(v_groove_angle / 2.0))

result = Box(bar_length, bar_width, bar_height)

with BuildPart() as gp:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((-v_groove_half_width, bar_height), (0, bar_height - v_groove_depth), (v_groove_half_width, bar_height), close=True)
        make_face()
    extrude(amount=bar_length)
groove = Pos(0, -bar_width/2, 0) * gp.part
result = result - groove

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, bar_height * 2)

rib_count = int(bar_length // rib_spacing)
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, bar_height/2 - rib_height/2) * Box(rib_width, bar_width - 2*chamfer_size, rib_height)
    result = result + rib

x_edges = result.edges().filter_by(Axis.X)
result = chamfer(x_edges, chamfer_size)

part = result
part.name = "v_groove_bar"
export_step(part, "output.step")
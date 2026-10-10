from build123d import *
import math

outer_radius = 30.0
inner_radius = 20.0
thickness = 5.7
tab_length = 15.0
tab_width = 10.0
hole_diameter = 5.4
chamfer_angle_deg = 20.0
chamfer_distance = thickness * math.tan(math.radians(chamfer_angle_deg))

base = Cylinder(outer_radius, thickness)
tab = Pos(outer_radius, 0, 0) * Box(tab_length, tab_width, thickness)
tabs = tab + Rot(0, 0, 90) * tab + Rot(0, 0, 180) * tab + Rot(0, 0, 270) * tab
result = base + tabs
result = result - Cylinder(inner_radius, thickness)

hole_positions = [
    (outer_radius + tab_length / 2, 0),
    (-(outer_radius + tab_length / 2), 0),
    (0, outer_radius + tab_length / 2),
    (0, -(outer_radius + tab_length / 2)),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, thickness)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "flanged_disc_with_tabs"
export_step(part, "output.step")
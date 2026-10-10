from build123d import *
import math

outer_diameter = 57.1
inner_diameter = 41.9
thickness = 5.7
tab_width = 11.4
tab_length = 15.0
tab_hole_diameter = 5.4
chamfer_distance = 1.9
outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

base = Cylinder(outer_radius, thickness) - Cylinder(inner_radius, thickness)

tab = Pos(outer_radius + tab_length / 2.0, 0, 0) * Box(tab_length, tab_width, thickness)
tab = tab - Pos(outer_radius + tab_length / 2.0, 0, 0) * Cylinder(tab_hole_diameter / 2.0, thickness)

tabs = tab
for i in range(1, 4):
    tabs = tabs + Rot(0, 0, i * 90) * tab

result = base + tabs
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "ring_with_tabs"
export_step(part, "output.step")
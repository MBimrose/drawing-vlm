from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 40.0
thickness = 6.0
tab_width = 12.0
tab_length = 20.0
hole_diameter = 5.0
chamfer_angle_deg = 30.0
chamfer_distance = thickness * math.tan(math.radians(chamfer_angle_deg))
pocket_width = 30.0
pocket_height = 15.0
pocket_depth = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, thickness) - Cylinder(inner_radius, thickness)

tab = Pos(outer_radius, 0, 0) * Box(tab_length, tab_width, thickness)
tabs = tab
for angle in [90, 180, 270]:
    tabs = tabs + Rot(0, 0, angle) * tab

result = result + tabs

hole = Pos(outer_radius, 0, 0) * Cylinder(hole_diameter / 2, thickness)
holes = hole
for angle in [90, 180, 270]:
    holes = holes + Rot(0, 0, angle) * hole

result = result - holes

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

pocket = Pos(0, 0, thickness - pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)
result = result - pocket

part = result
part.name = "ring_with_tabs"
export_step(part, "output.step")
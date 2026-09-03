from build123d import *

outer_diameter = 60.0
inner_diameter = 44.0
collar_length = 30.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
keyway_width = 6.0
keyway_depth = wall_thickness * 0.8
set_screw_diameter = 5.0
set_screw_head_diameter = 9.0
set_screw_head_depth = 3.0
rib_height = 5.0
rib_thickness = 2.0
rib_count = 4
chamfer_distance = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, collar_length) - Cylinder(inner_radius, collar_length)

keyway = Pos(inner_radius - keyway_depth / 2.0, 0, 0) * Box(keyway_depth, collar_length, keyway_width)
result = result - keyway

set_screw_hole = Pos(outer_radius - wall_thickness / 2.0, 0, 0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, wall_thickness)
result = result - set_screw_hole

set_screw_head = Pos(outer_radius - set_screw_head_depth / 2.0, 0, 0) * Rot(0, 90, 0) * Cylinder(set_screw_head_diameter / 2.0, set_screw_head_depth)
result = result - set_screw_head

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_thickness / 2.0, 0, 0) * Box(rib_thickness, rib_height, collar_length)
    result = result + rib

pocket = Pos(0, outer_radius - wall_thickness / 2.0, 0) * Box(collar_length * 0.6, wall_thickness, 6.0)
result = result - pocket

part = result
part.name = "collar_with_keyway"
export_step(part, "output.step")
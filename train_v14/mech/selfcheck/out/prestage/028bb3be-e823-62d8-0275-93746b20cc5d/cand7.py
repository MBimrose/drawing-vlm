from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
collar_length = 20.0
tooth_height = 5.0
tooth_width = 4.0
tooth_count = 12
set_screw_diameter = 2.0
set_screw_offset_angle = 45.0
groove_width = 3.0
groove_depth = 2.0
groove_position = 10.0
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius
set_screw_radius = inner_radius + wall_thickness / 2.0

result = Cylinder(outer_radius, collar_length)
result = result - Cylinder(inner_radius, collar_length)

for i in range(tooth_count):
    angle = i * 360.0 / tooth_count
    tooth = Pos(outer_radius + tooth_height / 2.0, 0, collar_length / 2.0) * Rot(0, 0, angle) * Box(tooth_width, tooth_height, collar_length)
    result = result + tooth

set_screw_hole = Pos(set_screw_radius, 0, collar_length / 2.0) * Rot(0, 0, set_screw_offset_angle) * Cylinder(set_screw_diameter / 2.0, collar_length * 2)
result = result - set_screw_hole

groove = Pos(0, 0, groove_position + groove_width / 2.0) * Cylinder(inner_radius - groove_depth, groove_width)
result = result - groove

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "gear_collar"
export_step(part, "output.step")
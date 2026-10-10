from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 30.0
collar_height = 20.0
split_gap_width = 2.0
slot_width = 4.0
slot_length = 12.0
slot_depth = (outer_diameter - inner_diameter) / 2 - 2.0
set_screw_diameter = 4.0
set_screw_head_diameter = 8.0
set_screw_head_depth = 3.0
chamfer_distance = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius

result = Cylinder(outer_radius, collar_height) - Cylinder(inner_radius, collar_height)

split_cut = Pos(0, 0, collar_height / 2) * Box(outer_diameter, split_gap_width, collar_height)
result = result - split_cut

for angle in [0, 90, 180, 270]:
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_width, slot_length)
    result = result - slot

set_screw_hole = Pos(outer_radius - wall_thickness / 2.0, 0, 0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, wall_thickness)
result = result - set_screw_hole

counterbore = Pos(outer_radius - set_screw_head_depth / 2.0, 0, 0) * Rot(0, 90, 0) * Cylinder(set_screw_head_diameter / 2.0, set_screw_head_depth)
result = result - counterbore

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "split_collar"
export_step(part, "output.step")
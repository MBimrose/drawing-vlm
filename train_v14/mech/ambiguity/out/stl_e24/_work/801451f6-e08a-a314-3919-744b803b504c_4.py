from build123d import *

bracket_length = 80
bracket_width = 40
bracket_thickness = 8
central_hole_dia = 20
groove_width = 3
groove_depth = 2
slot_length = 30
slot_width = 8
slot_offset = 20
mount_hole_dia = 4
mount_hole_offset = 12
rib_width = 6
rib_length = 20
rib_height = 4
chamfer_dist = 1

result = Box(bracket_length, bracket_width, bracket_thickness)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_dist)
result = result - Cylinder(central_hole_dia/2, bracket_thickness)

groove_outer_radius = central_hole_dia/2 + groove_width
groove_inner_radius = central_hole_dia/2
groove_z = bracket_thickness/2 - groove_depth - groove_depth/2
result = result - Pos(0, 0, groove_z) * Cylinder(groove_outer_radius, groove_depth)
result = result + Pos(0, 0, groove_z) * Cylinder(groove_inner_radius, groove_depth)

result = result - Pos(-slot_offset, 0, 0) * Box(slot_length, slot_width, bracket_thickness)
result = result - Pos(slot_offset, 0, 0) * Box(slot_length, slot_width, bracket_thickness)

result = result - Pos(0, mount_hole_offset, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, bracket_length)
result = result - Pos(0, -mount_hole_offset, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, bracket_length)

rib_z = bracket_thickness + rib_height/2
result = result + Pos(-bracket_length/4, 0, rib_z) * Box(rib_width, rib_length, rib_height)
result = result + Pos(bracket_length/4, 0, rib_z) * Box(rib_width, rib_length, rib_height)

part = result
part.name = "bracket"
export_step(part, "output.step")
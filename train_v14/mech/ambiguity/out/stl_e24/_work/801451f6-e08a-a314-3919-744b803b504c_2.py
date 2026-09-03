from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
central_hole_dia = 20.0
counterbore_dia = 30.0
counterbore_depth = 3.0
slot_width = 8.0
slot_length = 30.0
slot_offset = 12.0
mount_hole_dia = 4.0
mount_hole_offset = 12.0
rib_width = 6.0
rib_length = 20.0
rib_height = 4.0
chamfer_dist = 1.0

result = Box(bracket_length, bracket_width, bracket_thickness)
result = result - Cylinder(central_hole_dia / 2, bracket_thickness)
result = result - Pos(0, 0, bracket_thickness / 2 - counterbore_depth / 2) * Cylinder(counterbore_dia / 2, counterbore_depth)

for y_off in [slot_offset, -slot_offset]:
    result = result - Pos(0, y_off, 0) * Box(slot_length, slot_width, bracket_thickness)

for y_off in [mount_hole_offset, -mount_hole_offset]:
    result = result - Pos(0, y_off, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_dia / 2, bracket_length)

for x_off in [-bracket_length / 4, bracket_length / 4]:
    result = result + Pos(x_off, 0, bracket_thickness + rib_height / 2) * Box(rib_width, rib_length, rib_height)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_dist)

part = result
part.name = "bracket"
export_step(part, "output.step")
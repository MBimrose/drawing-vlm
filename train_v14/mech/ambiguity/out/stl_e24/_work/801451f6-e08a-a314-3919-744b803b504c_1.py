from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
central_hole_dia = 16.0
counterbore_dia = 24.0
counterbore_depth = 4.0
slot_width = 8.0
slot_length = 30.0
slot_offset = 15.0
mount_hole_dia = 4.0
mount_hole_offset = 12.0
rib_width = 6.0
rib_length = 20.0
rib_height = 4.0
rib_spacing = 40.0
chamfer_size = 1.0

solid_body = Box(bracket_length, bracket_width, bracket_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

solid_body = solid_body - Cylinder(central_hole_dia/2, bracket_thickness)
solid_body = solid_body - Pos(0, 0, bracket_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_dia/2, counterbore_depth)

solid_body = solid_body - Pos(slot_offset, 0, 0) * Box(slot_length, slot_width, bracket_thickness)

for x in [bracket_length/2, -bracket_length/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, bracket_length)

for x in [-rib_spacing/2, rib_spacing/2]:
    solid_body = solid_body + Pos(x, 0, bracket_thickness + rib_height/2) * Box(rib_width, rib_length, rib_height)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")
from build123d import *

outer_radius = 30.0
inner_radius = 8.0
collar_length = 20.0
keyway_width = 4.0
keyway_depth = 6.0
set_screw_diameter = 4.0
set_screw_depth = 8.0
set_screw_offset = outer_radius - 2.0
chamfer_size = 1.0

solid_body = Cylinder(outer_radius, collar_length) - Cylinder(inner_radius, collar_length)
solid_body = chamfer(solid_body.edges(), chamfer_size)

keyway = Pos(inner_radius - keyway_depth / 2.0, 0, 0) * Box(keyway_depth, keyway_width, collar_length)
solid_body = solid_body - keyway

set_screw_hole = Pos(set_screw_offset, set_screw_depth / 2.0, 0) * Rot(90, 0, 0) * Cylinder(set_screw_diameter / 2.0, set_screw_depth)
solid_body = solid_body - set_screw_hole

slot = Pos(outer_radius - 2.0, 0, -collar_length / 4.0) * Box(4.0, collar_length / 2.0, 4.0)
solid_body = solid_body - slot

part = solid_body
part.name = "collar_with_keyway_and_set_screw"
export_step(part, "output.step")
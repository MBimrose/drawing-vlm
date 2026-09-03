from build123d import *

outer_diameter = 80.0
wall_thickness = 5.0
length = 20.0
keyway_width = 6.0
keyway_depth = wall_thickness * 0.8
set_screw_diameter = 3.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

keyway_box = Pos(outer_radius - keyway_depth / 2.0, 0, 0) * Box(keyway_depth, keyway_width, length)
solid_body = solid_body - keyway_box

set_screw_cyl = Pos(outer_radius - wall_thickness / 2.0, 0, 0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, wall_thickness + 0.2)
solid_body = solid_body - set_screw_cyl

part = solid_body
part.name = "hollow_cylinder_with_keyway_and_set_screw"
export_step(part, "output.step")
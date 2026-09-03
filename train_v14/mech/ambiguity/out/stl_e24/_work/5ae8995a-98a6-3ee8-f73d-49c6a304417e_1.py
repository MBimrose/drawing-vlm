from build123d import *

outer_diameter = 30.0
inner_diameter = 20.0
length = 70.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
keyway_width = 4.0
keyway_depth = wall_thickness * 0.6
keyway_length = length * 0.7
set_screw_diameter = 4.0
set_screw_head_diameter = 6.0
set_screw_head_depth = 5.0
set_screw_offset = length * 0.5
chamfer_size = 2.0

outer_cyl = Cylinder(outer_diameter / 2.0, length)
inner_cyl = Cylinder(inner_diameter / 2.0, length)
solid_body = outer_cyl - inner_cyl

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

keyway_box = Pos(0, outer_diameter / 2.0 - keyway_depth / 2.0, 0) * Box(keyway_width, keyway_depth, keyway_length)
solid_body = solid_body - keyway_box

set_screw_cyl = Pos(0, outer_diameter / 2.0 - set_screw_head_depth / 2.0, set_screw_offset) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, set_screw_head_depth)
solid_body = solid_body - set_screw_cyl

part = solid_body
part.name = "hollow_shaft_with_keyway"
export_step(part, "output.step")
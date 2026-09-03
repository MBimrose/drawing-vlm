from build123d import *

outer_diameter = 30.0
inner_diameter = 20.0
length = 70.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
keyway_width = 4.0
keyway_depth = wall_thickness * 0.8
keyway_length = length * 0.7
set_screw_diameter = 5.0
set_screw_head_diameter = 9.0
set_screw_head_depth = 3.0
set_screw_offset = length * 0.25
chamfer_size = 2.0

solid_body = Cylinder(outer_diameter / 2.0, length) - Cylinder(inner_diameter / 2.0, length)

keyway_box = Pos(0, inner_diameter / 2.0 + keyway_depth / 2.0, 0) * Box(keyway_width, keyway_depth, keyway_length)
solid_body = solid_body - keyway_box

shaft_hole = Pos(0, outer_diameter / 2.0, set_screw_offset) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, outer_diameter)
cbore_hole = Pos(0, outer_diameter / 2.0 - set_screw_head_depth / 2.0, set_screw_offset) * Rot(0, 90, 0) * Cylinder(set_screw_head_diameter / 2.0, set_screw_head_depth)
solid_body = solid_body - shaft_hole - cbore_hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_shaft_with_keyway"
export_step(part, "output.step")
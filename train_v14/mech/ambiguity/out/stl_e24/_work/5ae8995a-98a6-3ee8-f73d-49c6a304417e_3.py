from build123d import *

sleeve_length = 70.0
outer_diameter = 30.0
inner_diameter = 20.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
keyway_width = 4.0
keyway_depth = wall_thickness * 0.6
keyway_length = sleeve_length * 0.7
set_screw_diameter = 5.0
set_screw_depth = wall_thickness * 0.8
set_screw_offset = sleeve_length * 0.3
chamfer_distance = 2.0

solid_body = Cylinder(outer_diameter / 2.0, sleeve_length) - Cylinder(inner_diameter / 2.0, sleeve_length)

keyway_box = Pos(0, outer_diameter / 2.0 - keyway_depth / 2.0, 0) * Box(keyway_width, keyway_depth, keyway_length)
solid_body = solid_body - keyway_box

set_screw_cyl = Pos(0, outer_diameter / 2.0 - set_screw_depth / 2.0, set_screw_offset) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, set_screw_depth)
solid_body = solid_body - set_screw_cyl

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

part = solid_body
part.name = "sleeve_with_keyway_and_set_screw"
export_step(part, "output.step")
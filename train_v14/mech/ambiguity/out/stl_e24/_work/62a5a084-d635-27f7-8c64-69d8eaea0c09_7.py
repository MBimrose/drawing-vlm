from build123d import *

outer_diameter = 30.0
inner_diameter = 12.0
collar_length = 20.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
set_screw_diameter = 6.0
set_screw_head_diameter = 10.0
set_screw_head_depth = 4.0
keyway_width = 4.0
keyway_depth = wall_thickness * 0.6
chamfer_size = 0.5
rib_thickness = 2.0
rib_height = collar_length * 0.4
rib_count = 3
rib_angle = 360.0 / rib_count

solid_body = Pos(0, 0, collar_length/2) * Cylinder(outer_diameter/2, collar_length)
solid_body = solid_body - Pos(0, 0, collar_length/2) * Cylinder(inner_diameter/2, collar_length)

keyway_box = Pos(outer_diameter/2 - keyway_depth/2, 0, 0) * Box(keyway_depth, keyway_width, collar_length)
solid_body = solid_body - keyway_box

set_screw_cyl = Pos(outer_diameter/2 - wall_thickness/2, 0, collar_length/2) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, wall_thickness + 2)
solid_body = solid_body - set_screw_cyl

set_screw_head = Pos(outer_diameter/2 - set_screw_head_depth/2, 0, collar_length/2) * Rot(0, 90, 0) * Cylinder(set_screw_head_diameter/2, set_screw_head_depth)
solid_body = solid_body - set_screw_head

for i in range(rib_count):
    angle = i * rib_angle
    rib = Rot(0, 0, angle) * Pos(outer_diameter/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, collar_length, rib_height)
    solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "collar_with_ribs"
export_step(part, "output.step")
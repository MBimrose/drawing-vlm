from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
length = 100.0
counterbore_diameter = 60.0
counterbore_depth = 10.0
keyway_width = 12.0
keyway_depth = 8.0
keyway_length = 40.0
keyway_offset = 30.0
chamfer_size = 2.0
mount_hole_diameter = 15.0
mount_hole_offset = 30.0
rib_thickness = 5.0
rib_width = 20.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
counterbore_radius = counterbore_diameter / 2.0
mount_hole_radius = mount_hole_diameter / 2.0
rib_outer_radius = outer_radius + rib_thickness

solid_body = Cylinder(outer_radius, length)
solid_body = solid_body - Cylinder(inner_radius, length)
solid_body = solid_body - Pos(0, 0, length/2 - counterbore_depth/2) * Cylinder(counterbore_radius, counterbore_depth)
solid_body = solid_body - Pos(outer_radius - keyway_depth/2, keyway_offset, 0) * Box(keyway_depth, keyway_width, keyway_length)
solid_body = solid_body - Pos(outer_radius - keyway_depth/2, mount_hole_offset, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_radius, keyway_depth)
solid_body = solid_body + Pos(0, 0, 0) * Cylinder(rib_outer_radius, rib_width)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
chamfer_edges = top_face.edges() + bottom_face.edges()
solid_body = chamfer(chamfer_edges, chamfer_size)

part = solid_body
part.name = "shaft_with_keyway_and_rib"
export_step(part, "output.step")
from build123d import *

outer_diameter = 50.0
inner_diameter = 21.0
thickness = 10.0
keyway_width = 5.0
keyway_depth = 6.0
chamfer_size = 0.8
mount_hole_diameter = 4.5
mount_hole_spacing = 30.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, thickness)
solid_body = solid_body - Cylinder(inner_radius, thickness)

slot_center_x = outer_radius - keyway_depth / 2.0
slot = Pos(slot_center_x, 0, 0) * Box(keyway_width, keyway_depth, thickness)
solid_body = solid_body - slot

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

for x in [-mount_hole_spacing / 2.0, mount_hole_spacing / 2.0]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_diameter / 2.0, thickness)

part = solid_body
part.name = "collar_with_keyway"
export_step(part, "output.step")
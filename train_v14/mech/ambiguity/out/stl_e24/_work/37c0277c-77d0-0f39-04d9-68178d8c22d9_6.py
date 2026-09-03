from build123d import *

outer_diameter = 50.0
inner_diameter = 21.0
thickness = 10.0
key_width = 5.0
key_depth = 4.0
mount_hole_diameter = 4.5
mount_hole_spacing = 30.0
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, thickness)
solid_body = solid_body - Cylinder(inner_radius, thickness)

keyway = Pos(inner_radius + key_depth / 2.0, 0, 0) * Box(key_width, key_depth, thickness)
solid_body = solid_body - keyway

for x in [-mount_hole_spacing / 2.0, mount_hole_spacing / 2.0]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_diameter / 2.0, thickness)

part = solid_body
part.name = "pulley_with_keyway"
export_step(part, "output.step")
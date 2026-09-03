from build123d import *

outer_radius = 30.0
inner_radius = 20.0
height = 70.0
groove_width = 5.0
groove_depth = 2.0
groove_center_z = 30.0
fillet_radius = 2.0
mount_hole_dia = 5.0
mount_hole_spacing = 50.0

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

groove_cutter = Pos(0, 0, groove_center_z - groove_width / 2) * Cylinder(inner_radius - groove_depth, groove_width)
solid_body = solid_body - groove_cutter

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_dia / 2, height)

part = solid_body
part.name = "XMountSocket"
export_step(part, "output.step")
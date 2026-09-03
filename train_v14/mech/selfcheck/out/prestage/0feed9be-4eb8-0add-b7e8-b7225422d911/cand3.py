from build123d import *

outer_radius = 30.0
inner_radius = 20.0
length = 70.0
wall_thickness = outer_radius - inner_radius
blind_bore_diameter = 12.0
blind_bore_depth = 20.0
fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 50.0

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)
solid_body = solid_body - Pos(0, 0, length - blind_bore_depth/2) * Cylinder(blind_bore_diameter/2, blind_bore_depth)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)
for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, length)

part = solid_body
part.name = "hollow_cylinder_with_bores"
export_step(part, "output.step")
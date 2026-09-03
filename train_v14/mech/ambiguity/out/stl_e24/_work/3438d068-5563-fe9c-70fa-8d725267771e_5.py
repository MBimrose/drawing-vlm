from build123d import *

outer_diameter = 30.0
inner_diameter = 12.0
collar_length = 15.0
blind_hole_depth = 10.0
chamfer_size = 1.0
mount_hole_diameter = 5.0
mount_hole_spacing = 12.0
rib_width = 4.0
rib_height = 3.0
rib_thickness = 2.0

solid_body = Cylinder(outer_diameter/2, collar_length)
solid_body = solid_body - Pos(0, 0, collar_length - blind_hole_depth/2) * Cylinder(inner_diameter/2, blind_hole_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for y in [mount_hole_spacing/2, -mount_hole_spacing/2]:
    solid_body = solid_body - Pos(outer_diameter/2, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_diameter)

rib = Pos(outer_diameter/2, 0, 0) * Box(rib_thickness, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "collar_with_rib"
export_step(part, "output.step")
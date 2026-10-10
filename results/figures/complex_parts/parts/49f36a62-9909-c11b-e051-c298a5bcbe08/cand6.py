from build123d import *

outer_diameter = 38.0
inner_diameter = 19.6
height = 16.0
split_width = 1.0
chamfer_size = 0.5
mount_hole_diameter = 3.0
mount_hole_spacing = 20.0
rib_height = 2.0
rib_thickness = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

split_cut = Pos(0, 0, height/2) * Box(split_width, outer_diameter, height)
solid_body = solid_body - split_cut

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, height/2) * Cylinder(mount_hole_diameter/2, height)

rib = Pos(0, 0, height/2 + rib_height/2) * (Cylinder(outer_radius, rib_height) - Cylinder(outer_radius - rib_thickness, rib_height))
solid_body = solid_body + rib

part = solid_body
part.name = "split_ring_with_rib"
export_step(part, "output.step")
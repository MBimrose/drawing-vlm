from build123d import *

outer_radius = 30.0
inner_radius = 20.0
length = 70.0
wall_thickness = outer_radius - inner_radius
groove_width = 8.0
groove_depth = 4.0
fillet_radius = 2.0
mount_hole_dia = 5.0
mount_hole_spacing = 50.0

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

groove_cutter = Pos(0, 0, length - groove_width / 2) * Cylinder(inner_radius - groove_depth, groove_width)
solid_body = solid_body - groove_cutter

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_dia / 2, length)

part = solid_body
part.name = "hollow_cylinder_with_groove_and_mount_holes"
export_step(part, "output.step")
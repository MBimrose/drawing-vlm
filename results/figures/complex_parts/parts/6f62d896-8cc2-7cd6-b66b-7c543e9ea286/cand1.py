from build123d import *

outer_diameter = 74.2
inner_diameter = 8.0
thickness = 10.0
counterbore_diameter = 9.0
counterbore_depth = 4.0
groove_width = 2.0
groove_depth = 1.5
chamfer_size = 0.5
rib_width = 4.0
rib_height = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
counterbore_radius = counterbore_diameter / 2.0
groove_outer_radius = outer_radius - groove_width / 2.0
groove_inner_radius = groove_outer_radius - groove_depth

solid_body = Cylinder(outer_radius, thickness)
solid_body = solid_body - Cylinder(inner_radius, thickness)
solid_body = solid_body - Pos(0, 0, thickness/2 - counterbore_depth/2) * Cylinder(counterbore_radius, counterbore_depth)

groove_cut = Cylinder(groove_outer_radius, groove_depth) - Cylinder(groove_inner_radius, groove_depth)
solid_body = solid_body - Pos(0, 0, thickness/2 - groove_depth/2) * groove_cut

rib = Pos(outer_radius, 0, 0) * Box(rib_width, rib_height, thickness)
solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "washer_with_rib"
export_step(part, "output.step")
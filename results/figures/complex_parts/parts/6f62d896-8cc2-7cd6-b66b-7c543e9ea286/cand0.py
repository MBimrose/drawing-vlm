from build123d import *

outer_diameter = 74.2
inner_diameter = 8.0
thickness = 10.0
rib_width = 5.0
rib_height = 3.0
chamfer_size = 0.5
counterbore_diameter = 9.0
counterbore_depth = 4.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, thickness)
solid_body = solid_body - Cylinder(inner_radius, thickness)

rib = Pos(outer_radius, 0, 0) * Box(rib_width, rib_height, thickness)
solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

solid_body = solid_body - Pos(0, 0, thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

part = solid_body
part.name = "flanged_disc_with_rib"
export_step(part, "output.step")
from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 20.0
tab_width = 20.0
tab_height = 10.0
hole_diameter = 8.0
hole_spacing = 30.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

base = Cylinder(outer_radius, thickness)
tab = Pos(0, outer_radius, 0) * Box(tab_width, tab_height, thickness)
solid_body = base + tab

solid_body = solid_body - Cylinder(inner_radius, thickness)

for x, y in [(-hole_spacing / 2.0, 0), (hole_spacing / 2.0, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2.0, thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "flanged_disc_with_tabs"
export_step(part, "output.step")
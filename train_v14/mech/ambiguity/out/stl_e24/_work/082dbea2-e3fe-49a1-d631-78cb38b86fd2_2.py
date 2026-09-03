from build123d import *

solid_body = Box(30, 20, 10)
solid_body = solid_body - Cylinder(2.5, 10)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, 1)

part = solid_body
part.name = "filleted_box_with_hole"
export_step(part, "output.step")
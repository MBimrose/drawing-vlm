from build123d import *

outer_width = 80.0
outer_depth = 60.0
height = 20.0
wall_thickness = 5.0
inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness
fillet_radius = 3.0
chamfer_distance = 2.0
center_hole_diameter = 5.0

solid_body = Box(outer_width, outer_depth, height) - Box(inner_width, inner_depth, height)
solid_body = solid_body - Cylinder(center_hole_diameter / 2, height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "XMountSocket"
export_step(part, "output.step")
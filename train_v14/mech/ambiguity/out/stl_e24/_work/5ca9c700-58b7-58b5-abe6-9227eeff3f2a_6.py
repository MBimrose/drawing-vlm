from build123d import *

outer_width = 80
outer_height = 60
length = 100
wall_thickness = 4
chamfer_size = 1
hole_diameter = 8

solid_body = Box(outer_width, outer_height, length)
solid_body = solid_body - Cylinder(hole_diameter / 2, length)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "chamfered_box_with_hole"
export_step(part, "output.step")
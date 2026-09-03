from build123d import *

tube_length = 100.0
outer_diameter = 40.0
wall_thickness = 3.0
groove_width = 30.0
groove_depth = 1.5
groove_position = tube_length / 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, tube_length) - Cylinder(inner_radius, tube_length)

groove_box = Pos(outer_radius - groove_depth / 2.0, 0, 0) * Box(groove_depth, groove_depth, groove_width)
solid_body = solid_body - groove_box

part = solid_body
part.name = "tube_with_groove"
export_step(part, "output.step")
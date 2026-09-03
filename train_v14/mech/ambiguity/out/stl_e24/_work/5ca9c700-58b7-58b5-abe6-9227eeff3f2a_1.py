from build123d import *

outer_width = 80.0
outer_height = 60.0
length = 100.0
wall_thickness = 5.0
chamfer_size = 1.0
hole_diameter = 8.0
hole_spacing = 30.0
hole_offset = 15.0

solid_body = Box(outer_width, outer_height, length)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)
solid_body = solid_body - Cylinder(hole_diameter/2, length)

part = solid_body
part.name = "chamfered_box_with_hole"
export_step(part, "output.step")
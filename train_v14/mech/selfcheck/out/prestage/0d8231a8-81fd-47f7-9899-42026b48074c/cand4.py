from build123d import *

outer_width = 50.0
outer_length = 80.0
outer_height = 30.0
wall_thickness = 3.0
chamfer_size = 1.0

solid_body = Box(outer_width, outer_length, outer_height)
solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "chamfered_box"
export_step(part, "output.step")
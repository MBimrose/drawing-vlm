from build123d import *

block_width = 50
block_length = 80
block_height = 30
chamfer_size = 1

solid_body = Box(block_width, block_length, block_height)
solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "chamfered_block"
export_step(part, "output.step")
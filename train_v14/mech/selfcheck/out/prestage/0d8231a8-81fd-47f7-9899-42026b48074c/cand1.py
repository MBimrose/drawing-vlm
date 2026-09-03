from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_width, block_length)
    extrude(amount=block_height)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "chamfered_block"
export_step(part, "output.step")
from build123d import *

block_length = 80.0
block_width = 50.0
block_thickness = 20.0
step_height = 10.0
step_width = 30.0
fillet_radius = 3.0

with BuildPart() as p:
    with BuildSketch() as s:
        with BuildLine() as l:
            Polyline((0,0), (block_length,0), (block_length,block_thickness),
                     (block_length-step_width,block_thickness),
                     (block_length-step_width-step_height,block_thickness+step_height),
                     (0,block_thickness+step_height), close=True)
        make_face()
    extrude(amount=block_width)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)
part = solid_body
part.name = "stepped_block"
export_step(part, "output.step")
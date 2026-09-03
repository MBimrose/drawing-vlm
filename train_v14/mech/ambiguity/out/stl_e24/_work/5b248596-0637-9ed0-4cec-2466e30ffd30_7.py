from build123d import *

with BuildPart() as p:
    Box(80, 30, 10)
solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), 2)
part = solid_body
part.name = "chamfered_box"
export_step(part, "output.step")
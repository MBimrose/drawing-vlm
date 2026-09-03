from build123d import *

with BuildPart() as p:
    Box(80, 30, 10)
solid_body = p.part
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, 2)
part = solid_body
part.name = "chamfered_box"
export_step(part, "output.step")
from build123d import *

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(50, 50)
    extrude(amount=8)

solid_body = p.part
solid_body = solid_body - Cylinder(6, 16)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, 2)

part = solid_body
part.name = "chamfered_box_with_hole"
export_step(part, "output.step")
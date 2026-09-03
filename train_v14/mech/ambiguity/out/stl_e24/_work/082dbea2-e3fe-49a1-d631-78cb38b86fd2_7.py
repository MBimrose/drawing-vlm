from build123d import *

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(30, 20)
    extrude(amount=10)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, 5) * Cylinder(2.5, 20)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, 1)

part = solid_body
part.name = "filleted_box_with_hole"
export_step(part, "output.step")
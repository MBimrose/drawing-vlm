from build123d import *

jaw_length = 80
jaw_width = 30
jaw_thickness = 10
chamfer_dist = 2

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(jaw_length, jaw_width)
    extrude(amount=jaw_thickness)

solid_body = p.part
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_dist)

part = solid_body
part.name = "jaw"
export_step(part, "output.step")
from build123d import *

arm_length = 80
arm_width = 30
arm_thickness = 10
chamfer_dist = 2

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(arm_length, arm_width)
    extrude(amount=arm_thickness)

solid_body = p.part
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_dist)

part = solid_body
part.name = "chamfered_arm"
export_step(part, "output.step")
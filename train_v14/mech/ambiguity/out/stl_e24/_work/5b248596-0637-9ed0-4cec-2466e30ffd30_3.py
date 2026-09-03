from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
chamfer_dist = 2.0

solid_body = Box(arm_length, arm_width, arm_thickness)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_dist)

part = solid_body
part.name = "chamfered_arm"
export_step(part, "output.step")
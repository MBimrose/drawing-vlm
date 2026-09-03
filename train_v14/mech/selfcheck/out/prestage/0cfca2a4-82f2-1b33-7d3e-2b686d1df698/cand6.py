from build123d import *

arm_length = 80.0
arm_width = 25.0
arm_thickness = 5.0
arc_radius = 30.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (arm_length, 0))
            l2 = Line(l1 @ 1, (arm_length, arm_width))
            l3 = Line(l2 @ 1, (0, arm_width))
            RadiusArc(l3 @ 1, (0, 0), arc_radius)
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)
solid_body = chamfer(solid_body.edges().sort_by(Axis.X)[-1:], chamfer_distance)

part = solid_body
part.name = "arm"
export_step(part, "output.step")
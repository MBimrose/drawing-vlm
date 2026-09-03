from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
tip_radius = arm_width / 2.0
hole_diameter = 7.5
hole_offset = 50.0
pocket_width = 12.0
pocket_height = 6.0
pocket_offset = 70.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (arm_width, 0))
            l2 = Line(l1 @ 1, (arm_width, arm_length - tip_radius))
            arc = ThreePointArc(l2 @ 1, (arm_width / 2.0, arm_length + tip_radius), (0, arm_length - tip_radius))
            l3 = Line(arc @ 1, (0, 0))
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = solid_body - Pos(arm_width / 2.0, hole_offset, 0) * Cylinder(hole_diameter / 2.0, arm_thickness * 2)
solid_body = solid_body - Pos(arm_width / 2.0, pocket_offset, 0) * Box(pocket_width, pocket_height, arm_thickness * 2)

part = solid_body
part.name = "arm_with_hole_and_pocket"
export_step(part, "output.step")
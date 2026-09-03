from build123d import *

arm_length = 80.0
arm_width = 15.0
arm_thickness = 8.0
flange_length = 30.0
notch_radius = 6.0
hole_diameter = 4.0
hole_offset = 20.0
chamfer_size = 1.0
rib_height = 3.0
rib_width = 10.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (arm_length, 0))
            l2 = Line(l1 @ 1, (arm_length + flange_length, 0))
            l3 = Line(l2 @ 1, (arm_length + flange_length, arm_width - notch_radius))
            arc = ThreePointArc(l3 @ 1, (arm_length + flange_length - notch_radius, arm_width - notch_radius), (arm_length + flange_length - notch_radius, arm_width))
            l4 = Line(arc @ 1, (0, arm_width))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

rib = Pos(arm_length / 2, arm_width / 2, arm_thickness / 2) * Box(rib_width, arm_width, rib_height)
solid_body = solid_body + rib

hole1 = Pos(hole_offset, arm_width / 2, arm_thickness / 2) * Cylinder(hole_diameter / 2, arm_thickness + 1)
hole2 = Pos(arm_length + flange_length - hole_offset, arm_width / 2, arm_thickness / 2) * Cylinder(hole_diameter / 2, arm_thickness + 1)
solid_body = solid_body - hole1 - hole2

part = solid_body
part.name = "arm_with_flange"
export_step(part, "output.step")
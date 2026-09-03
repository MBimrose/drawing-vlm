from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
tip_radius = arm_width / 2.0
hole_diameter = 7.5
hole_offset = 50.0
slot_width = 12.0
slot_height = 6.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-arm_width/2, 0), (-arm_width/2, arm_length - tip_radius))
            a1 = ThreePointArc(l1@1, (0, arm_length + tip_radius), (arm_width/2, arm_length - tip_radius))
            l2 = Line(a1@1, (arm_width/2, 0))
            l3 = Line(l2@1, l1@0)
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = solid_body - Pos(0, hole_offset, arm_thickness/2) * Cylinder(hole_diameter/2, arm_thickness + 1)
solid_body = solid_body - Pos(0, arm_length, arm_thickness/2) * Box(slot_width, slot_height, arm_thickness + 1)

part = solid_body
part.name = "arm_with_hole_and_slot"
export_step(part, "output.step")
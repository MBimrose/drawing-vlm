from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
fillet_radius = 2.0
hole_diameter = 7.5
hole_offset = 30.0
slot_width = 6.0
slot_length = 12.0
slot_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (arm_width, 0))
            l2 = Line(l1 @ 1, (arm_width, arm_length))
            arc = ThreePointArc(l2 @ 1, (arm_width / 2, arm_length + 10), (0, arm_length))
            l3 = Line(arc @ 1, (0, 0))
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

solid_body = solid_body - Pos(arm_width / 2, hole_offset, 0) * Cylinder(hole_diameter / 2, arm_thickness * 2)

slot_center_y = arm_length + 5 - slot_offset
solid_body = solid_body - Pos(arm_width / 2, slot_center_y, 0) * Box(slot_length, slot_width, arm_thickness * 2)

part = solid_body
part.name = "arm_with_hole_and_slot"
export_step(part, "output.step")
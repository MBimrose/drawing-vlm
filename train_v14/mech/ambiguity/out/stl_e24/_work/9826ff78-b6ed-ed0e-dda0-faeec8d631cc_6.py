from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
tip_radius = arm_width / 2.0
fillet_radius = 2.0
hole_diameter = 7.5
hole_offset = 30.0
slot_width = 12.0
slot_height = 6.0
slot_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((-arm_width/2, 0), (arm_width/2, 0))
            l2 = Line(l1@1, (arm_width/2, arm_length - tip_radius))
            arc = ThreePointArc(l2@1, (0, arm_length + tip_radius), (-arm_width/2, arm_length - tip_radius))
            l3 = Line(arc@1, l1@0)
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

solid_body = solid_body - Pos(0, hole_offset + tip_radius, arm_thickness/2) * Cylinder(hole_diameter/2, arm_thickness)

slot_y = arm_length + tip_radius - slot_offset - slot_height/2
solid_body = solid_body - Pos(0, slot_y, arm_thickness/2) * Box(slot_width, slot_height, arm_thickness)

part = solid_body
part.name = "arm_with_hole_and_slot"
export_step(part, "output.step")
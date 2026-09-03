from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
fillet_radius = 5.0
slot_width = 12.0
slot_height = 6.0
slot_offset = 4.0
hole_diameter = 7.5
hole_offset = 30.0
base_fillet = 2.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (arm_width, 0))
            l2 = Line(l1 @ 1, (arm_width, arm_length - fillet_radius))
            arc = ThreePointArc(l2 @ 1, (arm_width / 2, arm_length + fillet_radius), (0, arm_length - fillet_radius))
            l3 = Line(arc @ 1, (0, 0))
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), base_fillet)

slot_box = Pos(arm_width / 2, arm_length - slot_offset - slot_height / 2, arm_thickness / 2) * Box(slot_width, slot_height, arm_thickness)
solid_body = solid_body - slot_box

hole_cyl = Pos(arm_width / 2, arm_length - hole_offset, arm_thickness / 2) * Cylinder(hole_diameter / 2, arm_thickness)
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "arm_with_slot_and_hole"
export_step(part, "output.step")
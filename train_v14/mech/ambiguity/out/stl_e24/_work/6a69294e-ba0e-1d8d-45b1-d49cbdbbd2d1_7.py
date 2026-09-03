from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
notch_width = 15.0
notch_depth = 8.0
rib_width = 10.0
rib_height = 5.0
rib_thickness = 2.0
hole_diameter = 4.0
hole_spacing = 12.0
hole_offset_from_end = 15.0
chamfer_distance = 1.0
slot_width = 2.0
slot_length = 12.0
slot_spacing = 10.0
slot_count = 5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (arm_length, 0))
            l2 = Line(l1 @ 1, (arm_length, arm_width - notch_depth))
            l3 = Line(l2 @ 1, (arm_length - notch_width, arm_width))
            l4 = Line(l3 @ 1, (0, arm_width))
            l5 = Line(l4 @ 1, (0, 0))
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

rib = Pos(arm_length / 2, arm_width / 2, arm_thickness - rib_height / 2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

for i in range(3):
    x = hole_offset_from_end + i * hole_spacing
    solid_body = solid_body - Pos(x, arm_width / 2, arm_thickness / 2) * Cylinder(hole_diameter / 2, arm_thickness + 1)

for i in range(slot_count):
    x = hole_offset_from_end + i * slot_spacing
    solid_body = solid_body - Pos(x, arm_width / 2, arm_thickness - arm_thickness / 4) * Box(slot_length, slot_width, arm_thickness / 2)

part = solid_body
part.name = "arm_with_notch_rib_holes_slots"
export_step(part, "output.step")
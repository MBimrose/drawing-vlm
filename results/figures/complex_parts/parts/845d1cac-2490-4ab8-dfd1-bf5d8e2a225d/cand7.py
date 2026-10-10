from build123d import *

arm_length = 80.0
arm_width = 10.0
arm_thickness = 6.0
boss_diameter = 12.0
boss_length = 20.0
slot_length = 30.0
slot_width_near = 4.0
slot_width_far = 8.0
slot_offset = 10.0
hole_diameter = 4.0
chamfer_size = 0.5
rib_height = 3.0
rib_width = 4.0
rib_spacing = 20.0

base = Pos(0, 0, arm_thickness/2) * Box(arm_length, arm_width, arm_thickness)
boss = Pos(arm_length/2 - boss_length/2, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_length)
result = base + boss

slot_center_x = arm_length/2 - slot_offset - slot_length/2
with BuildPart() as slot_bp:
    with BuildSketch(Plane.XY.offset(arm_thickness)) as slot_sk:
        with BuildLine() as slot_line:
            Polyline(
                (slot_center_x - slot_length/2, -slot_width_near/2),
                (slot_center_x + slot_length/2, -slot_width_far/2),
                (slot_center_x + slot_length/2, slot_width_far/2),
                (slot_center_x - slot_length/2, slot_width_near/2),
                close=True
            )
        make_face()
    extrude(amount=-arm_thickness)
result = result - slot_bp.part

result = result - Pos(slot_center_x, 0, arm_thickness/2) * Cylinder(hole_diameter/2, arm_thickness)

rib_count = int((arm_length - 2*slot_offset) // rib_spacing)
for i in range(rib_count):
    rib_x = slot_offset + i * rib_spacing
    result = result - Pos(rib_x, 0, arm_thickness - rib_height/2) * Box(rib_width, rib_height, rib_height)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "arm_with_boss_and_slot"
export_step(part, "output.step")
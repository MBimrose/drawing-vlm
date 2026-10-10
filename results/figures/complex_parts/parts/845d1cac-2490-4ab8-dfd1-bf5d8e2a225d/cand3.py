from build123d import *

arm_length = 80.0
arm_width = 10.0
arm_thickness = 5.0
slot_length = 30.0
slot_width_start = 8.0
slot_width_end = 4.0
slot_offset = 10.0
boss_diameter = 12.0
boss_length = 20.0
chamfer_dist = 0.5
hole_diameter = 4.0
hole_offset = 15.0

base = Pos(arm_length/2, 0, 0) * Box(arm_length, arm_width, arm_thickness)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        with BuildLine() as slot_line:
            Polyline(
                (slot_offset, -slot_width_start/2),
                (slot_offset + slot_length, -slot_width_end/2),
                (slot_offset + slot_length, slot_width_end/2),
                (slot_offset, slot_width_start/2),
                close=True
            )
        make_face()
    extrude(amount=arm_thickness)
slot_solid = slot_bp.part

result = base - slot_solid

boss = Pos(arm_length + boss_length/2, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_length)
result = result + boss

hole = Pos(hole_offset, 0, 0) * Cylinder(hole_diameter/2, arm_thickness * 2)
result = result - hole

part = result
part.name = "arm_with_slot_boss_and_hole"
export_step(part, "output.step")
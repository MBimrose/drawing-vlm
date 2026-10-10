from build123d import *

arm_length = 80.0
arm_width = 10.0
arm_thickness = 5.0
slot_length = 60.0
slot_width_start = 8.0
slot_width_end = 4.0
slot_offset = 10.0
boss_diameter = 12.0
boss_length = 20.0
chamfer_size = 0.5
hole_diameter = 4.0
pocket_length = 15.0
pocket_width = 6.0
pocket_depth = 2.0
rib_thickness = 2.0
rib_width = 8.0
rib_height = 2.0

base = Pos(0, 0, arm_thickness/2) * Box(arm_length, arm_width, arm_thickness)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        with BuildLine() as slot_line:
            Polyline(
                (-slot_length/2, -slot_width_start/2),
                (slot_length/2, -slot_width_end/2),
                (slot_length/2, slot_width_end/2),
                (-slot_length/2, slot_width_start/2),
                close=True
            )
        make_face()
    extrude(amount=arm_thickness)
slot_solid = Pos(slot_offset, 0, 0) * slot_bp.part

result = base - slot_solid

boss = Pos(arm_length/2 - boss_length/2, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_length)
result = result + boss

result = result - Pos(0, 0, arm_thickness/2) * Cylinder(hole_diameter/2, arm_thickness)

result = result - Pos(0, arm_width/2 - pocket_depth/2, arm_thickness/2) * Box(pocket_length, pocket_depth, pocket_width)

result = result + Pos(0, -arm_width/2 + rib_thickness/2, rib_height/2) * Box(rib_width, rib_thickness, rib_height)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "arm_with_slot_boss"
export_step(part, "output.step")
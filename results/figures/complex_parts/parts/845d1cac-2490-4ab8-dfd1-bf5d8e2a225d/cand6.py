from build123d import *

arm_length = 80.0
arm_width = 10.0
arm_thickness = 6.0
boss_diameter = 12.0
boss_length = 20.0
slot_start_width = 2.0
slot_end_width = 6.0
slot_length = 40.0
slot_offset = 30.0
hole_diameter = 4.0
hole_offset_x = 20.0
hole_offset_y = 3.0
chamfer_size = 0.5
pocket_width = 12.0
pocket_depth = 4.0
pocket_height = 2.0

base = Pos(arm_length/2, 0, 0) * Box(arm_length, arm_width, arm_thickness)
boss = Pos(arm_length - boss_length/2, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_length)
result = base + boss

with BuildPart() as slot_bp:
    with BuildSketch(Plane.YZ) as slot_sk:
        with BuildLine() as slot_line:
            Polyline((0, -slot_start_width/2), (0, slot_start_width/2),
                     (slot_length, slot_end_width/2), (slot_length, -slot_end_width/2), close=True)
        make_face()
    extrude(amount=arm_thickness)
slot_solid = Pos(slot_offset, 0, 0) * slot_bp.part
result = result - slot_solid

hole = Pos(hole_offset_x, hole_offset_y, 0) * Cylinder(hole_diameter/2, arm_thickness + 2)
result = result - hole

pocket = Pos(arm_length/2, arm_width/2 - pocket_depth/2, pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
result = result - pocket

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "arm_with_boss_slot_hole_pocket"
export_step(part, "output.step")
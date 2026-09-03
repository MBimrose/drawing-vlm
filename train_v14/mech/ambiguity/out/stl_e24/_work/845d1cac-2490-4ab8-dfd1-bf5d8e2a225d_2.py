from build123d import *

arm_length = 80.0
arm_width_base = 15.0
arm_width_tip = 8.0
arm_thickness = 6.0
boss_diameter = 12.0
boss_length = 20.0
slot_width = 3.0
slot_length = 15.0
slot_offset = 30.0
chamfer_dist = 0.5
rib_width = 4.0
rib_height = 3.0
rib_spacing = 10.0
rib_thickness = 2.0
hole_diameter = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Polygon((0, -arm_width_base/2), (0, arm_width_base/2), (arm_length, arm_width_tip/2), (arm_length, -arm_width_tip/2))
    extrude(amount=arm_thickness)

solid_body = p.part
solid_body = solid_body + Pos(arm_length, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_length)
solid_body = solid_body - Pos(slot_offset + slot_length/2, arm_width_base/2 - arm_thickness/2, arm_thickness/2) * Box(slot_length, arm_thickness, slot_width)
solid_body = solid_body - Pos(arm_length + boss_length/2, 0, 0) * Cylinder(hole_diameter/2, arm_thickness + boss_length + 10)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_dist)

num_ribs = int((arm_length - 20) // rib_spacing)
for i in range(num_ribs):
    x_pos = 10 + i * rib_spacing
    solid_body = solid_body + Pos(x_pos, 0, rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)

part = solid_body
part.name = "tapered_arm_with_boss"
export_step(part, "output.step")
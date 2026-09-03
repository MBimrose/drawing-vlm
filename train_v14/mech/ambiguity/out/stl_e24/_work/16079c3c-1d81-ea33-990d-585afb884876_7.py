from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 6.0
boss_diameter = 12.0
boss_height = 8.0
slot_width = 20.0
slot_depth = 4.0
hole_diameter = 4.0
fillet_radius = 1.0
chamfer_distance = 0.7

base = Pos(0, 0, arm_length/2) * Box(arm_width, arm_thickness, arm_length)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)
base = chamfer(base.edges().filter_by(Axis.Y), chamfer_distance)

boss = Pos(0, arm_thickness/2, 0) * Rot(90, 0, 0) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

slot = Pos(0, -arm_thickness/2 + slot_depth/2, arm_length/2) * Box(slot_width, slot_depth, arm_length)
result = result - slot

hole = Pos(0, -arm_thickness/2 + arm_length/2, arm_length/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, arm_length)
result = result - hole

part = result
part.name = "arm_with_boss_slot_hole"
export_step(part, "output.step")
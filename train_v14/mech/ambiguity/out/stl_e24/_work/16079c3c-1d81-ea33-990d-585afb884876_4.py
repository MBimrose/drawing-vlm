from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 6.0
boss_diameter = 12.0
boss_height = 6.0
boss_offset_x = 0.0
boss_offset_y = -arm_thickness/2 + boss_diameter/2 - 2.0
fillet_radius = 1.0
chamfer_distance = 0.7
hole_diameter = 4.0
hole_offset_x = 0.0
hole_offset_y = 0.0
rib_width = 12.0
rib_thickness = 2.0
notch_width = 10.0
notch_depth = 2.0

base = Pos(0, 0, arm_length/2) * Box(arm_width, arm_thickness, arm_length)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)
base = chamfer(base.edges().filter_by(Axis.X), chamfer_distance)

boss = Pos(boss_offset_x, boss_offset_y, 0) * Rot(90, 0, 0) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

hole = Pos(hole_offset_x, hole_offset_y, arm_length/2) * Cylinder(hole_diameter/2, arm_length + 20)
result = result - hole

rib = Pos(0, arm_thickness/2 + rib_thickness/2, arm_length/2) * Box(rib_width, rib_thickness, arm_length)
result = result + rib

notch = Pos(0, arm_thickness/2 + rib_thickness - notch_depth/2, arm_length/2) * Box(notch_width, notch_depth, arm_length)
result = result - notch

part = result
part.name = "arm_with_boss_rib_notch"
export_step(part, "output.step")
from build123d import *
import math

gear_outer_radius = 30.0
gear_inner_radius = 5.0
gear_thickness = 10.0
tooth_count = 12
tooth_height = 4.0
tooth_width = 6.0
tooth_chamfer = 0.5
boss_radius = 8.0
boss_height = 5.0

gear_body = Cylinder(gear_outer_radius, gear_thickness)
gear_body = gear_body - Cylinder(gear_inner_radius, gear_thickness)

boss = Pos(0, 0, gear_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
gear_body = gear_body + boss

tooth = Pos(gear_inner_radius + tooth_height/2, 0, gear_thickness/2 + boss_height/2) * Box(tooth_width, tooth_height, boss_height)
tooth = chamfer(tooth.edges().filter_by(Axis.Z), tooth_chamfer)

for i in range(tooth_count):
    angle = i * 360.0 / tooth_count
    gear_body = gear_body + Rot(0, 0, angle) * tooth

part = gear_body
part.name = "gear_with_teeth"
export_step(part, "output.step")
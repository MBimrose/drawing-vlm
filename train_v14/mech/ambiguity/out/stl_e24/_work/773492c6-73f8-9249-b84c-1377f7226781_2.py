from build123d import *
import math

gear_outer_radius = 30.0
gear_inner_radius = 8.0
gear_height = 12.0
tooth_count = 20
tooth_width = 4.0
tooth_height = 6.0
tooth_depth = 2.0

base = Cylinder(gear_outer_radius, gear_height)
bore = Cylinder(gear_inner_radius, gear_height)
gear_body = base - bore

tooth = Pos(gear_inner_radius + tooth_height / 2.0, 0, gear_height / 2.0) * Box(tooth_width, tooth_height, tooth_depth)

gear_with_teeth = gear_body
for i in range(tooth_count):
    angle = i * 360.0 / tooth_count
    rotated_tooth = Rot(0, 0, angle) * tooth
    gear_with_teeth = gear_with_teeth + rotated_tooth

part = gear_with_teeth
part.name = "gear_with_teeth"
export_step(part, "output.step")
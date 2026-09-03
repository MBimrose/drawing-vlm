from build123d import *
import math

gear_outer_radius = 30.0
gear_thickness = 10.0
shaft_radius = 8.0
tooth_width = 4.0
tooth_height = 6.0
num_teeth = 24

gear_body = Cylinder(gear_outer_radius, gear_thickness)
gear_body = gear_body - Cylinder(shaft_radius, gear_thickness)

for i in range(num_teeth):
    angle = math.radians(i * 360.0 / num_teeth)
    px = gear_outer_radius * math.cos(angle)
    py = gear_outer_radius * math.sin(angle)
    tooth = Pos(px, py, gear_thickness / 2) * Rot(0, 0, math.degrees(angle)) * Box(tooth_width, tooth_height, gear_thickness / 2)
    gear_body = gear_body + tooth

part = gear_body
part.name = "gear_with_teeth"
export_step(part, "output.step")
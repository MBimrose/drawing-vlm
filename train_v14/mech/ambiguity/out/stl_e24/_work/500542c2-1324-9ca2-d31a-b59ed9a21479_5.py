from build123d import *
import math

gear_radius = 30.0
gear_thickness = 10.0
num_teeth = 20
tooth_height = 8.0
tooth_width = 6.0
center_hole_diameter = 6.0
relief_width = 12.0
relief_depth = 2.0

gear_body = Cylinder(gear_radius, gear_thickness)

tooth_radius = gear_radius + tooth_height / 2
for i in range(num_teeth):
    angle = math.radians(i * 360.0 / num_teeth)
    px = tooth_radius * math.cos(angle)
    py = tooth_radius * math.sin(angle)
    tooth = Pos(px, py, gear_thickness / 2) * Rot(0, 0, math.degrees(angle)) * Box(tooth_height, tooth_width, gear_thickness)
    gear_body = gear_body + tooth

gear_body = gear_body - Cylinder(center_hole_diameter / 2, gear_thickness * 2)

relief_box = Pos(0, 0, gear_thickness - relief_depth / 2) * Box(relief_width, relief_width, relief_depth)
gear_body = gear_body - relief_box

part = gear_body
part.name = "gear"
export_step(part, "output.step")
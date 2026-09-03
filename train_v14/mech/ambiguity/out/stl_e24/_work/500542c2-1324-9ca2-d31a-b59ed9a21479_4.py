from build123d import *
import math

gear_base_radius = 30.0
gear_thickness = 10.0
tooth_height = 8.0
tooth_width = 6.0
num_teeth = 20
central_hole_diameter = 6.0

gear = Cylinder(gear_base_radius, gear_thickness)

for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    tooth = Rot(0, 0, angle) * Pos(gear_base_radius, 0, gear_thickness / 2) * Box(tooth_height, tooth_width, gear_thickness)
    gear = gear + tooth

gear = gear - Cylinder(central_hole_diameter / 2, gear_thickness * 2)

part = gear
part.name = "gear"
export_step(part, "output.step")
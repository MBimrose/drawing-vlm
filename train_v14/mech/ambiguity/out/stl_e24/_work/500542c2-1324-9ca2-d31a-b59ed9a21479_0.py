from build123d import *
import math

gear_module = 3.0
num_teeth = 20
pitch_diameter = gear_module * num_teeth
pitch_radius = pitch_diameter / 2.0
addendum = gear_module
dedendum = 1.25 * gear_module
outer_radius = pitch_radius + addendum
root_radius = pitch_radius - dedendum
gear_thickness = 10.0
bore_diameter = 6.0
tooth_width = (2 * math.pi * pitch_radius) / num_teeth * 0.6

base = Cylinder(root_radius, gear_thickness)
tooth = Pos(root_radius + addendum / 2.0, 0, gear_thickness / 2.0) * Box(addendum, tooth_width, gear_thickness)

gear = base
for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    gear = gear + Rot(0, 0, angle) * tooth

gear = gear - Cylinder(bore_diameter / 2, gear_thickness * 2)

part = gear
part.name = "gear"
export_step(part, "output.step")
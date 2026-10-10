from build123d import *
import math

module = 1.5
pressure_angle_deg = 20
tooth_count = 52
gear_thickness = 10.0
hub_radius = 15.0
counterbore_dia = 8.0
counterbore_depth = 4.0
chamfer_size = 0.5

addendum = module
dedendum = 1.25 * module
pitch_radius = (module * tooth_count) / 2.0
root_radius = pitch_radius - dedendum
outer_radius = pitch_radius + addendum
tooth_height = addendum + dedendum
tooth_width = (3.14159 * module) / 2.0 * 0.9

result = Cylinder(root_radius, gear_thickness)
for i in range(tooth_count):
    angle = i * 360.0 / tooth_count
    tooth = Pos(root_radius + tooth_height/2.0, 0, 0) * Rot(0, 0, angle) * Box(tooth_height, tooth_width, gear_thickness)
    result = result + tooth

result = result + Cylinder(hub_radius, gear_thickness)

# Counterbore: wider recess at top, through-hole shaft
cbore_r = (counterbore_dia + 2*chamfer_size) / 2
shaft_r = counterbore_dia / 2
result = result - Pos(0, 0, gear_thickness/2 - counterbore_depth/2) * Cylinder(cbore_r, counterbore_depth)
result = result - Cylinder(shaft_r, gear_thickness)

part = result
part.name = "spur_gear"
export_step(part, OUTPUT_PATH)
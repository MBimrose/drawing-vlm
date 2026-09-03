from build123d import *
import math

gear_outer_radius = 30.0
gear_thickness = 10.0
num_teeth = 20
tooth_depth = 6.0
tooth_width = 8.0
tooth_height = gear_thickness + 5.0
center_hole_diameter = 6.0

base = Cylinder(gear_outer_radius, gear_thickness)
base = base - Cylinder(center_hole_diameter / 2, gear_thickness)

tooth = Pos(gear_outer_radius + tooth_depth / 2, 0, gear_thickness / 2) * Box(tooth_width, tooth_depth, tooth_height)

teeth = tooth
for i in range(1, num_teeth):
    angle = i * 360.0 / num_teeth
    teeth = teeth + Rot(0, 0, angle) * tooth

part = base + teeth
part.name = "gear_with_teeth"
export_step(part, "output.step")
from build123d import *
import math

hub_radius = 30.0
hub_thickness = 10.0
tooth_height = 5.0
tooth_width = 8.0
tooth_depth = 6.0
num_teeth = 20
keyway_width = 4.0
keyway_depth = 3.0
keyway_length = 20.0
central_hole_dia = 6.0

result = Cylinder(hub_radius, hub_thickness)
result = result - Cylinder(central_hole_dia / 2, hub_thickness)
result = result - Pos(hub_radius - keyway_depth / 2, 0, hub_thickness / 2) * Box(keyway_depth, keyway_width, keyway_length)

for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    tooth = Rot(0, 0, angle) * Pos(hub_radius + tooth_height / 2, 0, hub_thickness / 2) * Box(tooth_width, tooth_depth, hub_thickness + tooth_height)
    result = result + tooth

part = result
part.name = "gear_with_teeth"
export_step(part, "output.step")
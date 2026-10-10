from build123d import *
import math

base_radius = 30.0
tooth_height = 8.0
tooth_width = 6.0
overlap = 1.0
gear_thickness = 10.0
num_teeth = 20
central_hole_dia = 6.0
pocket_radius = 12.0
pocket_depth = 4.0
chamfer_size = 0.5

result = Cylinder(base_radius, gear_thickness)

for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    angle_rad = math.radians(angle)
    dist = base_radius - overlap + tooth_height / 2
    cx = dist * math.cos(angle_rad)
    cy = dist * math.sin(angle_rad)
    tooth = Pos(cx, cy, gear_thickness / 2) * Rot(0, 0, angle) * Box(tooth_height, tooth_width, gear_thickness)
    result = result + tooth

result = result - Cylinder(central_hole_dia / 2, gear_thickness)
result = result - Pos(0, 0, gear_thickness - pocket_depth / 2) * Cylinder(pocket_radius, pocket_depth)
result = chamfer(result.edges(), chamfer_size)

part = result
part.name = "gear_with_teeth"
export_step(part, OUTPUT_PATH)
from build123d import *
import math

gear_outer_radius = 30.0
gear_inner_radius = 8.0
gear_thickness = 10.0
tooth_height = 4.0
tooth_width = 6.0
tooth_count = 20
tooth_depth = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(gear_outer_radius)
    extrude(amount=gear_thickness)

solid_body = p.part
solid_body = solid_body - Cylinder(gear_inner_radius, gear_thickness * 2)

for i in range(tooth_count):
    angle = i * 360.0 / tooth_count
    tooth = Rot(0, 0, angle) * Pos(gear_outer_radius + tooth_depth / 2, 0, gear_thickness + tooth_depth / 2) * Box(tooth_width, tooth_height, tooth_depth)
    solid_body = solid_body + tooth

part = solid_body
part.name = "gear"
export_step(part, "output.step")
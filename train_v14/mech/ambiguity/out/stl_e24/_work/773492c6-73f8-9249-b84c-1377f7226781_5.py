from build123d import *
import math

gear_outer_radius = 30.0
gear_thickness = 12.0
bore_radius = 8.0
tooth_width = 4.0
tooth_height = 6.0
tooth_count = 24
tooth_overlap = 1.0

base = Cylinder(gear_outer_radius, gear_thickness)
bore = Cylinder(bore_radius, gear_thickness)
gear_body = base - bore

tooth_center_x = gear_outer_radius + tooth_height/2 - tooth_overlap
tooth = Pos(tooth_center_x, 0, gear_thickness/2) * Box(tooth_width, tooth_height, gear_thickness/2)

teeth = tooth
for i in range(1, tooth_count):
    angle = i * 360.0 / tooth_count
    teeth = teeth + Rot(0, 0, angle) * tooth

part = gear_body + teeth
part.name = "gear_with_teeth"
export_step(part, "output.step")
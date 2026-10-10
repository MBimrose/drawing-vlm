from build123d import *
import math

gear_base_radius = 30.0
gear_thickness = 10.0
num_teeth = 12
tooth_height = 5.0
pitch_angle = 2 * math.pi / num_teeth
tooth_angle = pitch_angle * 0.8
bore_diameter = 10.0
relief_depth = 2.0
relief_width_angle = tooth_angle * 0.5
chamfer_size = 0.5

result = Cylinder(gear_base_radius, gear_thickness)

p1 = (gear_base_radius * math.cos(-tooth_angle/2), gear_base_radius * math.sin(-tooth_angle/2))
p2 = ((gear_base_radius+tooth_height) * math.cos(-tooth_angle/2), (gear_base_radius+tooth_height) * math.sin(-tooth_angle/2))
p3 = ((gear_base_radius+tooth_height) * math.cos(tooth_angle/2), (gear_base_radius+tooth_height) * math.sin(tooth_angle/2))
p4 = (gear_base_radius * math.cos(tooth_angle/2), gear_base_radius * math.sin(tooth_angle/2))

with BuildPart() as tooth_bp:
    with BuildSketch() as s:
        Polygon(p1, p2, p3, p4)
    extrude(amount=gear_thickness)
tooth_solid = tooth_bp.part

for i in range(num_teeth):
    angle_deg = i * 360.0 / num_teeth
    result = result + Rot(0, 0, angle_deg) * tooth_solid

inner_r = gear_base_radius + tooth_height - relief_depth
outer_r = gear_base_radius + tooth_height
r1 = (inner_r * math.cos(-relief_width_angle/2), inner_r * math.sin(-relief_width_angle/2))
r2 = (outer_r * math.cos(-relief_width_angle/2), outer_r * math.sin(-relief_width_angle/2))
r3 = (outer_r * math.cos(relief_width_angle/2), outer_r * math.sin(relief_width_angle/2))
r4 = (inner_r * math.cos(relief_width_angle/2), inner_r * math.sin(relief_width_angle/2))

with BuildPart() as relief_bp:
    with BuildSketch() as s:
        Polygon(r1, r2, r3, r4)
    extrude(amount=gear_thickness)
relief_solid = relief_bp.part

for i in range(num_teeth):
    angle_deg = i * 360.0 / num_teeth
    result = result - Rot(0, 0, angle_deg) * relief_solid

result = result - Cylinder(bore_diameter/2, gear_thickness + 2)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "gear_with_teeth_and_reliefs"
export_step(part, OUTPUT_PATH)
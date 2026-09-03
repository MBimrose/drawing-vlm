from build123d import *
import math

gear_outer_radius = 40.0
gear_inner_radius = 20.0
gear_thickness = 15.0
num_teeth = 12
tooth_width = 5.0
tooth_height = 8.0
central_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_radius = 30.0
chamfer_distance = 0.5
relief_hole_diameter = 2.4
relief_hole_radius = gear_inner_radius - 7.0

gear_body = Cylinder(gear_outer_radius, gear_thickness)

for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    tooth = Rot(0, 0, angle) * Pos(gear_outer_radius, 0, 0) * Box(tooth_height, tooth_width, gear_thickness)
    gear_body = gear_body + tooth

gear_body = gear_body - Cylinder(central_hole_diameter / 2, gear_thickness)

for i in range(4):
    angle = i * 90.0
    x = mount_hole_radius * math.cos(math.radians(angle))
    y = mount_hole_radius * math.sin(math.radians(angle))
    gear_body = gear_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, gear_thickness)

for i in range(12):
    angle = i * 30.0
    x = relief_hole_radius * math.cos(math.radians(angle))
    y = relief_hole_radius * math.sin(math.radians(angle))
    gear_body = gear_body - Pos(x, y, gear_thickness / 4) * Cylinder(relief_hole_diameter / 2, gear_thickness / 2)

gear_body = chamfer(gear_body.edges().filter_by(Axis.Z), chamfer_distance)

part = gear_body
part.name = "gear_with_teeth"
export_step(part, "output.step")
from build123d import *
import math

outer_radius = 45.0
inner_radius = 10.0
thickness = 8.0
tooth_height = 5.0
tooth_width = 6.0
num_teeth = 20
split_gap = 2.0
mount_hole_dia = 4.0
mount_hole_radius = 30.0
mount_hole_count = 6

gear_body = Cylinder(outer_radius, thickness)
gear_body = gear_body - Cylinder(inner_radius, thickness)

for i in range(num_teeth):
    angle_deg = i * 360.0 / num_teeth
    tooth = Rot(0, 0, angle_deg) * Pos(outer_radius, 0, 0) * Box(tooth_width, tooth_height, thickness)
    gear_body = gear_body + tooth

split_cut = Box(2 * outer_radius, split_gap, thickness)
gear_body = gear_body - split_cut

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    gear_body = gear_body - Pos(px, py, 0) * Cylinder(mount_hole_dia / 2, thickness)

part = gear_body
part.name = "split_gear"
export_step(part, "output.step")
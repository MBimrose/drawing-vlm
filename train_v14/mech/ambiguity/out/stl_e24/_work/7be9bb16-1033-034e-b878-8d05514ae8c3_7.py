from build123d import *
import math

gear_outer_radius = 40.0
gear_inner_radius = 20.0
gear_thickness = 15.0
tooth_height = 8.0
tooth_width = 6.0
tooth_count = 12
central_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_radius = 30.0
blind_hole_diameter = 2.4
blind_hole_radius = 13.0
blind_hole_depth = gear_thickness / 2.0
chamfer_distance = 0.5

gear_body = Cylinder(gear_outer_radius, gear_thickness)

tooth = Pos(gear_outer_radius + tooth_height / 2.0, 0, 0) * Box(tooth_height, tooth_width, gear_thickness)
for i in range(tooth_count):
    angle = i * 360.0 / tooth_count
    gear_body = gear_body + Rot(0, 0, angle) * tooth

gear_body = gear_body - Cylinder(central_hole_diameter / 2, gear_thickness)

for i in range(4):
    angle = math.radians(i * 360.0 / 4)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    gear_body = gear_body - Pos(px, py, 0) * Cylinder(mount_hole_diameter / 2, gear_thickness)

for i in range(12):
    angle = math.radians(i * 360.0 / 12)
    px = blind_hole_radius * math.cos(angle)
    py = blind_hole_radius * math.sin(angle)
    gear_body = gear_body - Pos(px, py, gear_thickness / 2 - blind_hole_depth / 2) * Cylinder(blind_hole_diameter / 2, blind_hole_depth)

gear_body = chamfer(gear_body.edges().filter_by(Axis.Z), chamfer_distance)

part = gear_body
part.name = "gear"
export_step(part, "output.step")
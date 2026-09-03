from build123d import *
import math

gear_outer_radius = 40.0
gear_inner_radius = 20.0
gear_thickness = 15.0
tooth_height = 8.0
tooth_width = 6.0
num_teeth = 12
central_hole_diameter = 6.0
vent_hole_diameter = 2.4
vent_hole_radius = gear_inner_radius - 7.0
vent_hole_count = 12
mount_hole_diameter = 4.0
mount_hole_radius = 30.0
mount_hole_count = 4
chamfer_size = 0.5

gear_body = Cylinder(gear_outer_radius, gear_thickness)

tooth = Pos(gear_outer_radius + tooth_height/2, 0, 0) * Box(tooth_height, tooth_width, gear_thickness)
for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    gear_body = gear_body + Rot(0, 0, angle) * tooth

gear_body = gear_body - Cylinder(central_hole_diameter/2, gear_thickness)

for i in range(vent_hole_count):
    angle = math.radians(i * 360.0 / vent_hole_count)
    px = vent_hole_radius * math.cos(angle)
    py = vent_hole_radius * math.sin(angle)
    gear_body = gear_body - Pos(px, py, 0) * Cylinder(vent_hole_diameter/2, gear_thickness)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    gear_body = gear_body - Pos(px, py, 0) * Cylinder(mount_hole_diameter/2, gear_thickness)

gear_body = chamfer(gear_body.edges().filter_by(Axis.Z), chamfer_size)

part = gear_body
part.name = "gear_with_teeth_and_holes"
export_step(part, "output.step")
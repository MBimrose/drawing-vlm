from build123d import *
import math

gear_outer_diameter = 80.0
gear_thickness = 15.0
num_teeth = 12
tooth_width = 6.0
tooth_height = 8.0
tooth_overlap = 0.5
central_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_radius = 30.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 5.0
chamfer_distance = 0.5
vent_hole_diameter = 2.4
vent_hole_count = 12
vent_hole_radius = (gear_outer_diameter/2) - tooth_height - 5.0

gear_body = Cylinder(gear_outer_diameter/2, gear_thickness)

tooth_center_x = gear_outer_diameter/2 + tooth_height/2 - tooth_overlap
tooth = Pos(tooth_center_x, 0, 0) * Box(tooth_height, tooth_width, gear_thickness)

for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    gear_body = gear_body + Rot(0, 0, angle) * tooth

gear_body = gear_body - Cylinder(central_hole_diameter/2, gear_thickness)

for i in range(4):
    angle = i * 90.0
    x = mount_hole_radius * math.cos(math.radians(angle))
    y = mount_hole_radius * math.sin(math.radians(angle))
    gear_body = gear_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, gear_thickness)

gear_body = gear_body - Pos(0, 0, gear_thickness - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)

for i in range(vent_hole_count):
    angle = i * 360.0 / vent_hole_count
    x = vent_hole_radius * math.cos(math.radians(angle))
    y = vent_hole_radius * math.sin(math.radians(angle))
    gear_body = gear_body - Pos(x, y, 0) * Cylinder(vent_hole_diameter/2, gear_thickness)

gear_body = chamfer(gear_body.edges().filter_by(Axis.Z), chamfer_distance)

part = gear_body
part.name = "gear"
export_step(part, "output.step")
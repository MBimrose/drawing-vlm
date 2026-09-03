from build123d import *
import math

gear_outer_diameter = 80.0
gear_thickness = 15.0
num_teeth = 12
tooth_width = 6.0
tooth_height = 8.0
central_hole_diameter = 6.0
chamfer_size = 0.5
vent_hole_diameter = 2.4
vent_hole_count = 12
vent_hole_radius = gear_outer_diameter/2 - tooth_height - 5.0
mount_hole_diameter = 4.0
mount_hole_radius = gear_outer_diameter/2 - 10.0

gear = Cylinder(gear_outer_diameter/2, gear_thickness)

for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    tooth = Rot(0, 0, angle) * Pos(gear_outer_diameter/2 + tooth_height/2, 0, 0) * Box(tooth_height, tooth_width, gear_thickness)
    gear = gear + tooth

gear = gear - Cylinder(central_hole_diameter/2, gear_thickness)

for i in range(vent_hole_count):
    angle = i * 360.0 / vent_hole_count
    x = vent_hole_radius * math.cos(math.radians(angle))
    y = vent_hole_radius * math.sin(math.radians(angle))
    gear = gear - Pos(x, y, 0) * Cylinder(vent_hole_diameter/2, gear_thickness)

for i in range(4):
    angle = i * 360.0 / 4
    x = mount_hole_radius * math.cos(math.radians(angle))
    y = mount_hole_radius * math.sin(math.radians(angle))
    gear = gear - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, gear_thickness)

gear = chamfer(gear.edges().filter_by(Axis.Z), chamfer_size)

part = gear
part.name = "gear_with_teeth_and_holes"
export_step(part, "output.step")
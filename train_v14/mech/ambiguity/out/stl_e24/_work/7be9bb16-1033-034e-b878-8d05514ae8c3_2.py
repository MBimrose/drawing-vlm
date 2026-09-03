from build123d import *
import math

gear_outer_diameter = 80.0
gear_thickness = 15.0
num_teeth = 12
tooth_height = 8.0
tooth_width = 6.0
central_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_radius = 30.0
keyway_width = 5.0
keyway_depth = 10.0
chamfer_distance = 0.5
knurl_radius = 1.2
knurl_depth = gear_thickness / 2.0
knurl_count = 12

gear_body_radius = (gear_outer_diameter - 2 * tooth_height) / 2.0

result = Cylinder(gear_body_radius, gear_thickness)

for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    tooth = Rot(0, 0, angle) * Pos(gear_body_radius + tooth_height / 2.0, 0, 0) * Box(tooth_width, tooth_height, gear_thickness)
    result = result + tooth

result = result - Cylinder(central_hole_diameter / 2, gear_thickness)

for i in range(4):
    angle = i * 90.0
    x = mount_hole_radius * math.cos(math.radians(angle))
    y = mount_hole_radius * math.sin(math.radians(angle))
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, gear_thickness)

keyway = Pos(gear_body_radius + keyway_depth / 2.0, 0, 0) * Box(keyway_width, keyway_depth, gear_thickness)
result = result - keyway

for i in range(knurl_count):
    angle = i * 360.0 / knurl_count
    x = (gear_body_radius - knurl_depth - knurl_radius) * math.cos(math.radians(angle))
    y = (gear_body_radius - knurl_depth - knurl_radius) * math.sin(math.radians(angle))
    result = result - Pos(x, y, 0) * Cylinder(knurl_radius, knurl_depth)

top_face = result.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_distance)

part = result
part.name = "gear_with_teeth"
export_step(part, "output.step")
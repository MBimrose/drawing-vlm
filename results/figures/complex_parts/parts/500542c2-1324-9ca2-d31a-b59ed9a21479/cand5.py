from build123d import *
import math

gear_outer_radius = 30.0
gear_inner_radius = 15.0
gear_thickness = 10.0
num_teeth = 20
tooth_height = 8.0
tooth_width = 6.0
central_hole_diameter = 6.0
keyway_width = 4.0
keyway_depth = 3.0
chamfer_size = 0.5

gear_body = Cylinder(gear_outer_radius, gear_thickness)

tooth_radius = gear_outer_radius + tooth_height / 2
for i in range(num_teeth):
    angle = math.radians(i * 360.0 / num_teeth)
    px = tooth_radius * math.cos(angle)
    py = tooth_radius * math.sin(angle)
    tooth = Pos(px, py, gear_thickness / 2) * Rot(0, 0, math.degrees(angle)) * Box(tooth_height, tooth_width, gear_thickness)
    gear_body = gear_body + tooth

gear_body = gear_body - Cylinder(central_hole_diameter / 2, gear_thickness)

keyway = Pos(0, 0, gear_thickness - keyway_depth / 2) * Box(keyway_width, keyway_depth, keyway_depth)
gear_body = gear_body - keyway

vertical_edges = gear_body.edges().filter_by(Axis.Z)
gear_body = chamfer(vertical_edges, chamfer_size)

part = gear_body
part.name = "gear_with_teeth"
export_step(part, "output.step")
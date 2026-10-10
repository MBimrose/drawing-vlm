from build123d import *

outer_diameter = 60
body_length = 80
shaft_diameter = 20
shaft_length = 30
rib_width = 6
rib_height = 6
rib_count = 12
keyway_width = 4
keyway_depth = 8
chamfer_size = 1
central_hole_diameter = 10

outer_radius = outer_diameter / 2.0
shaft_radius = shaft_diameter / 2.0

import math

result = Pos(0, 0, body_length / 2) * Cylinder(outer_radius, body_length)
result = result + Pos(0, 0, -shaft_length / 2) * Cylinder(shaft_radius, shaft_length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius + rib_height / 2.0, 0, body_length / 2) * Box(rib_width, rib_height, body_length)
    result = result + rib

result = result - Pos(0, 0, (body_length - shaft_length) / 2) * Cylinder(central_hole_diameter / 2, body_length + shaft_length)

result = result - Pos(shaft_radius - keyway_depth / 2.0, 0, -shaft_length / 2) * Box(keyway_width, keyway_depth, shaft_length)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

part = result
part.name = "ribbed_shaft_with_keyway"
export_step(part, "output.step")
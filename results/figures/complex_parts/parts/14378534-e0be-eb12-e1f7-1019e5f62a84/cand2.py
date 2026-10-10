from build123d import *

outer_diameter = 30.0
outer_radius = outer_diameter / 2.0
body_length = 30.0
shaft_diameter = 10.0
shaft_radius = shaft_diameter / 2.0
shaft_length = 12.0
knurl_width = 2.0
knurl_height = 4.0
knurl_count = 12

body = Cylinder(outer_radius, body_length)
shaft = Pos(0, 0, body_length / 2 + shaft_length / 2) * Cylinder(shaft_radius, shaft_length)
result = body + shaft

for i in range(knurl_count):
    angle = i * 360.0 / knurl_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - knurl_width / 2.0, 0, body_length / 2) * Box(knurl_width, knurl_height, body_length)
    result = result + rib

hole = Pos(0, 0, shaft_length / 2) * Cylinder(shaft_radius, body_length + shaft_length)
result = result - hole

part = result
part.name = "knurled_shaft"
export_step(part, "output.step")
from build123d import *

outer_radius = 30
wall_thickness = 5
inner_radius = outer_radius - wall_thickness
length = 80
rib_width = 6
rib_height = 8
rib_count = 12
hole_diameter = 6
hole_offset = 15
shaft_radius = 10
shaft_length = 30
chamfer_distance = 1

body = Pos(0, 0, length/2) * (Cylinder(outer_radius, length) - Cylinder(inner_radius, length))

rib = Pos(outer_radius + rib_width/2, 0, length/2) * Box(rib_width, rib_height, length)
rib_pattern = rib
for i in range(1, rib_count):
    rib_pattern = rib_pattern + Rot(0, 0, i * 360 / rib_count) * rib

body = body + rib_pattern

hole = Pos(hole_offset, 0, length/2) * Cylinder(hole_diameter/2, length)
hole_pattern = hole
for i in range(1, 4):
    hole_pattern = hole_pattern + Rot(0, 0, i * 90) * hole

body = body - hole_pattern

shaft = Pos(0, 0, -shaft_length/2) * Cylinder(shaft_radius, shaft_length)
shaft = chamfer(shaft.edges(), chamfer_distance)

part = body + shaft
part.name = "ribbed_cylinder_with_shaft"
export_step(part, "output.step")
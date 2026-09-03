from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 40.0
length = 50.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
groove_width = 6.0
groove_depth = 4.0
groove_position = length / 2.0
rib_count = 6
rib_width = 10.0
rib_thickness = 4.0
rib_height = length
rib_offset = inner_diameter / 2.0 + rib_thickness / 2.0
hole_diameter = 8.0

result = Cylinder(outer_diameter / 2.0, length)
result = result - Cylinder(inner_diameter / 2.0, length)

groove_radius = (outer_diameter / 2.0) - groove_depth
result = result - Pos(0, 0, groove_position - groove_width / 2.0) * Cylinder(groove_radius, groove_width)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(rib_offset, 0, rib_height / 2.0) * Box(rib_width, rib_thickness, rib_height)
    result = result + rib

result = result - Pos(0, 0, length / 2.0) * Cylinder(hole_diameter / 2.0, length)

part = result
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")
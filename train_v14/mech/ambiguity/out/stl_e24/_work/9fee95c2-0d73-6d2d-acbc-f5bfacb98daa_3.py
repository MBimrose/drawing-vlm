from build123d import *

outer_radius = 30.0
inner_radius = 20.0
length = 50.0
groove_depth = 4.0
groove_width = 8.0
rib_count = 6
rib_thickness = 4.0
rib_length = 25.0
rib_width = 10.0

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

inner_groove = Cylinder(inner_radius, groove_width) - Cylinder(inner_radius - groove_depth, groove_width)
result = result - inner_groove

outer_groove = Cylinder(outer_radius, groove_width) - Cylinder(outer_radius - groove_depth, groove_width)
result = result - outer_groove

rib = Pos(inner_radius + rib_width / 2, 0, length / 2) * Box(rib_width, rib_thickness, rib_length)
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    result = result + Rot(0, 0, angle) * rib

part = result
part.name = "hollow_cylinder_with_grooves_and_ribs"
export_step(part, "output.step")
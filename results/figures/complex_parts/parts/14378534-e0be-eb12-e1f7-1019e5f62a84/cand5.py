from build123d import *
import math

outer_diameter = 30.0
inner_diameter = 10.0
length = 30.0
rib_height = 2.0
rib_width = 4.0
rib_length = 20.0
rib_count = 12
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, length)
result = result - Cylinder(inner_radius, length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_height / 2.0, 0, length / 2.0) * Box(rib_height, rib_width, rib_length)
    result = result + rib

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "ribbed_cylinder"
export_step(part, "output.step")
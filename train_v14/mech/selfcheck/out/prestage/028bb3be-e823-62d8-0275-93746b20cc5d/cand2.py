from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
height = 20.0
rib_width = 5.0
rib_height = 20.0
rib_depth = 5.0
rib_count = 12
set_screw_diameter = 2.0
set_screw_offset = 22.0
chamfer_size = 0.5

result = Cylinder(outer_diameter / 2, height)
result = result - Cylinder(inner_diameter / 2, height)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Pos(outer_diameter / 2 + rib_depth / 2, 0, height / 2) * Rot(0, 0, angle) * Box(rib_depth, rib_width, rib_height)
    result = result + rib

result = result - Pos(set_screw_offset, 0, 0) * Cylinder(set_screw_diameter / 2, height)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "ribbed_cylinder_with_set_screw"
export_step(part, "output.step")
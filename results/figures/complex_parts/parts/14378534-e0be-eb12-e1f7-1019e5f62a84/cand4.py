from build123d import *

outer_diameter = 30.0
inner_diameter = 10.0
spacer_length = 30.0
rib_height = 4.0
rib_width = 2.0
rib_count = 12
counterbore_diameter = 12.0
counterbore_depth = 6.0
chamfer_size = 1.0

result = Cylinder(outer_diameter / 2, spacer_length)
result = result - Cylinder(inner_diameter / 2, spacer_length)

rib = Pos(outer_diameter / 2 - rib_width / 2, 0, spacer_length / 2) * Box(rib_width, rib_height, spacer_length * 0.8)
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    result = result + Rot(0, 0, angle) * rib

result = result - Pos(0, 0, spacer_length - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

top_edges = result.edges().sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "ribbed_spacer"
export_step(part, "output.step")
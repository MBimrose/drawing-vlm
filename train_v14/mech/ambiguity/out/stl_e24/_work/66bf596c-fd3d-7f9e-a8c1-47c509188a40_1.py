from build123d import *

outer_diameter = 50.0
length = 30.0
bore_diameter = 12.0
knurl_height = 5.0
knurl_width = 2.0
knurl_count = 12
chamfer_size = 1.0
overlap = 0.5

base = Cylinder(outer_diameter / 2, length)
base = base - Cylinder(bore_diameter / 2, length)

top_face = base.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
base = chamfer(top_edges, chamfer_size)

knurl_block = Box(knurl_height, knurl_width, length / 2)
knurl_block = Pos(outer_diameter / 2 + knurl_height / 2 - overlap, 0, length / 4) * knurl_block

knurl_union = knurl_block
for i in range(1, knurl_count):
    angle = i * 360.0 / knurl_count
    rotated = Rot(0, 0, angle) * knurl_block
    knurl_union = knurl_union + rotated

result = base + knurl_union

part = result
part.name = "knurled_cylinder"
export_step(part, "output.step")
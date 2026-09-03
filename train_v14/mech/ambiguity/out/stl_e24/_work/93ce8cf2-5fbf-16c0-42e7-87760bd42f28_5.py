from build123d import *
import math

outer_diameter = 50.0
inner_diameter = 12.0
height = 20.0
counterbore_diameter = 13.5
counterbore_depth = 4.0
knurl_pitch = 5.0
knurl_width = 2.0
knurl_depth = 0.6
chamfer_size = 0.8
pocket_width = 10.0
pocket_height = 5.0
pocket_depth = 2.0

solid_body = Cylinder(outer_diameter / 2, height)
solid_body = solid_body - Cylinder(inner_diameter / 2, height)
solid_body = solid_body - Pos(0, 0, -height / 2 + counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, height / 2 - pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)

knurl_count = int((math.pi * outer_diameter) / knurl_pitch)
knurl_radius = outer_diameter / 2 - knurl_depth / 2
for i in range(knurl_count):
    angle = math.radians(i * 360.0 / knurl_count)
    px = knurl_radius * math.cos(angle)
    py = knurl_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Box(knurl_width, knurl_depth, knurl_depth)

part = solid_body
part.name = "knurled_bushing"
export_step(part, "output.step")
from build123d import *
import math

outer_diameter = 50.0
inner_diameter = 12.0
collar_length = 20.0
counterbore_diameter = 13.5
counterbore_depth = 5.0
knurl_pitch = 10.0
knurl_width = 2.0
knurl_height = 1.5
knurl_depth = 0.6
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
counterbore_radius = counterbore_diameter / 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=collar_length)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, collar_length/2) * Cylinder(inner_radius, collar_length)
solid_body = solid_body - Pos(0, 0, counterbore_depth/2) * Cylinder(counterbore_radius, counterbore_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

knurl_count = int(360 / knurl_pitch)
knurl_r = outer_radius - knurl_depth / 2
for i in range(knurl_count):
    angle = math.radians(i * knurl_pitch)
    px = knurl_r * math.cos(angle)
    py = knurl_r * math.sin(angle)
    solid_body = solid_body - Pos(px, py, collar_length/2 - knurl_depth/2) * Box(knurl_width, knurl_height, knurl_depth)

part = solid_body
part.name = "knurled_collar"
export_step(part, "output.step")
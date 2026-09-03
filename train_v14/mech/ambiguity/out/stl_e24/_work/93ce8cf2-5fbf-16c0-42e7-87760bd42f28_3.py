from build123d import *
import math

outer_diameter = 50.0
inner_diameter = 12.0
collar_length = 20.0
inlet_chamfer = 0.6
knurl_pitch = 10.0
knurl_width = 2.0
knurl_depth = 0.8
knurl_height = 1.5
counterbore_diameter = 13.5
counterbore_depth = 4.0

solid_body = Cylinder(outer_diameter / 2, collar_length)
solid_body = solid_body - Cylinder(inner_diameter / 2, collar_length)
solid_body = solid_body - Pos(0, 0, -collar_length / 2 + counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, inlet_chamfer)

knurl_count = int((math.pi * outer_diameter) / knurl_pitch)
knurl_r = outer_diameter / 2 - knurl_depth / 2
for i in range(knurl_count):
    angle = math.radians(i * 360.0 / knurl_count)
    px = knurl_r * math.cos(angle)
    py = knurl_r * math.sin(angle)
    knurl_box = Pos(px, py, 0) * Rot(0, 0, math.degrees(angle)) * Box(knurl_depth, knurl_width, knurl_height)
    solid_body = solid_body - knurl_box

part = solid_body
part.name = "knurled_collar"
export_step(part, "output.step")
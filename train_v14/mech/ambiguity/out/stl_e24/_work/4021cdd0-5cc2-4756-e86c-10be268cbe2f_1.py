from build123d import *

knob_diameter = 60.0
knob_height = 15.0
knurl_width = 2.0
knurl_height = 4.0
knurl_depth = 1.0
knurl_count = 12
blind_hole_diameter = 10.0
blind_hole_depth = 8.0
chamfer_size = 0.5

import math

solid_body = Cylinder(knob_diameter / 2, knob_height)

for i in range(knurl_count):
    angle = math.radians(i * 360.0 / knurl_count)
    px = (knob_diameter / 2 - knurl_depth / 2) * math.cos(angle)
    py = (knob_diameter / 2 - knurl_depth / 2) * math.sin(angle)
    knurl = Pos(px, py, knob_height / 2 + knurl_depth / 2) * Rot(0, 0, math.degrees(angle)) * Box(knurl_width, knurl_height, knurl_depth)
    solid_body = solid_body + knurl

hole = Pos(0, 0, knob_height / 2 - blind_hole_depth / 2) * Cylinder(blind_hole_diameter / 2, blind_hole_depth)
solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "knob_with_knurls"
export_step(part, "output.step")
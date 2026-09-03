from build123d import *

outer_diameter = 50.0
inner_diameter = 12.0
cap_height = 20.0
knurl_depth = 1.5
knurl_width = 2.0
knurl_height = 0.6
knurl_count = 30
chamfer_size = 0.5
counterbore_diameter = 13.5
counterbore_depth = 3.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid = Pos(0, 0, cap_height/2) * Cylinder(outer_radius, cap_height)
solid = solid - Pos(0, 0, cap_height/2) * Cylinder(inner_radius, cap_height)
solid = solid - Pos(0, 0, counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = chamfer(top_face.edges(), chamfer_size)

import math
for i in range(knurl_count):
    angle = math.radians(i * 360.0 / knurl_count)
    px = (outer_radius - knurl_depth/2) * math.cos(angle)
    py = (outer_radius - knurl_depth/2) * math.sin(angle)
    knurl = Pos(px, py, cap_height/2) * Rot(0, 0, math.degrees(angle)) * Box(knurl_depth, knurl_width, knurl_height)
    solid = solid - knurl

part = solid
part.name = "knurled_cap"
export_step(part, "output.step")
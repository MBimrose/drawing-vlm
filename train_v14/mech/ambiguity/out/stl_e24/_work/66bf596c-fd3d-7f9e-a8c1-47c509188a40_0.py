from build123d import *

knob_outer_radius = 25.0
knob_height = 30.0
central_hole_radius = 6.0
rib_width = 5.0
rib_height = 20.0
rib_thickness = 2.0
rib_count = 12
rib_overlap = 0.5
knurl_radius = 1.0
knurl_depth = 2.0
knurl_rows = 4
knurl_cols = 12
knurl_spacing = 4.0
chamfer_size = 0.8

import math

result = Cylinder(knob_outer_radius, knob_height)
result = result - Cylinder(central_hole_radius, knob_height)

rib_center_x = knob_outer_radius + rib_width / 2 - rib_overlap
rib = Pos(rib_center_x, 0, knob_height / 2) * Box(rib_width, rib_thickness, rib_height)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    result = result + Rot(0, 0, angle) * rib

for row in range(knurl_rows):
    for col in range(knurl_cols):
        x = (col - (knurl_cols - 1) / 2) * knurl_spacing
        y = (row - (knurl_rows - 1) / 2) * knurl_spacing
        result = result - Pos(x, y, knob_height - knurl_depth / 2) * Cylinder(knurl_radius, knurl_depth)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "knob"
export_step(part, "output.step")
from build123d import *

knob_outer_radius = 30.0
knob_height = 20.0
central_hole_diameter = 6.0
counterbore_diameter = 10.0
counterbore_depth = 4.0
tab_width = 25.0
tab_thickness = 8.0
tab_length = 40.0
knurl_depth = 1.0
knurl_width = 2.0
knurl_count = 24
chamfer_size = 0.8

import math

result = Cylinder(knob_outer_radius, knob_height)

tab = Pos(tab_thickness/2, tab_width/2, knob_height/2 + tab_length/2) * Box(tab_thickness, tab_width, tab_length)
result = result + tab

result = result - Cylinder(central_hole_diameter/2, knob_height + 10)

result = result - Pos(0, 0, knob_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

for i in range(knurl_count):
    angle = math.radians(i * 360.0 / knurl_count)
    px = (knob_outer_radius - knurl_depth/2) * math.cos(angle)
    py = (knob_outer_radius - knurl_depth/2) * math.sin(angle)
    knurl_cut = Pos(px, py, knob_height - knurl_depth/2) * Box(knurl_width, knurl_depth, knurl_depth)
    result = result - knurl_cut

top_face = result.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "knob_with_tab"
export_step(part, "output.step")
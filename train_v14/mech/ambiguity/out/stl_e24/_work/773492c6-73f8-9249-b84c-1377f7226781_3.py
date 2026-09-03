from build123d import *

knob_outer_radius = 30.0
knob_height = 12.0
shaft_radius = 8.0
knurl_rib_width = 4.0
knurl_rib_height = 6.0
knurl_rib_thickness = 2.0
knurl_count = 24
slot_width = 5.0
slot_height = 8.0
slot_offset = 20.0
chamfer_size = 0.5

import math

result = Cylinder(knob_outer_radius, knob_height)
result = result - Cylinder(shaft_radius, knob_height)

for i in range(knurl_count):
    angle = math.radians(i * 360.0 / knurl_count)
    px = (knob_outer_radius + knurl_rib_thickness / 2) * math.cos(angle)
    py = (knob_outer_radius + knurl_rib_thickness / 2) * math.sin(angle)
    rib = Pos(px, py, knob_height / 2) * Rot(0, 0, math.degrees(angle)) * Box(knurl_rib_width, knurl_rib_height, knurl_rib_thickness)
    result = result + rib

slot = Pos(slot_offset, 0, knob_height - knob_height / 4) * Box(slot_width, slot_height, knob_height / 2)
result = result - slot

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "knob_with_knurl_ribs"
export_step(part, "output.step")
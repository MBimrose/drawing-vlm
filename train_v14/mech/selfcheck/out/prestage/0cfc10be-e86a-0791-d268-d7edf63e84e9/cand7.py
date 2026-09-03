from build123d import *

knob_outer_radius = 30.0
knob_body_height = 20.0
rib_width = 8.0
rib_height = 25.0
rib_length = 40.0
central_hole_diameter = 6.0
counterbore_diameter = 10.0
counterbore_depth = 4.0
slot_width = 4.0
slot_depth = 2.0
slot_offset = 5.0
chamfer_size = 0.8

base = Cylinder(knob_outer_radius, knob_body_height)
rib = Pos(rib_width/2, rib_height/2, knob_body_height/2 + rib_length/2) * Box(rib_width, rib_height, rib_length)
result = base + rib

cbore = Pos(0, 0, knob_body_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
shaft = Pos(0, 0, 0) * Cylinder(central_hole_diameter/2, knob_body_height + 1)
result = result - cbore - shaft

slot = Pos(slot_offset, 0, knob_body_height/2 - slot_depth/2) * Box(slot_width, rib_height, slot_depth)
result = result - slot

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "knob_with_rib"
export_step(part, "output.step")
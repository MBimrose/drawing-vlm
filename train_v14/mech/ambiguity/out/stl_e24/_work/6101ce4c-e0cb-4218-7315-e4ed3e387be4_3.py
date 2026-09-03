from build123d import *

knob_width = 40.0
knob_height = 30.0
knob_thickness = 8.0
tab_width = 12.0
tab_height = 20.0
tab_fillet_radius = 2.0
blind_hole_diameter = 6.0
blind_hole_depth = 4.5
slot_width = 4.0
slot_length = 20.0
chamfer_distance = 0.8

base = Box(knob_width, knob_height, knob_thickness)
tab = Pos(knob_width/2 + tab_width/2, 0, 0) * Box(tab_width, tab_height, knob_thickness)
result = base + tab

result = fillet(result.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:], tab_fillet_radius)
result = chamfer(result.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2], chamfer_distance)

result = result - Pos(knob_width/2 + tab_width - blind_hole_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
result = result - Pos(knob_width/2 + tab_width - knob_thickness/2, 0, 0) * Box(knob_thickness, slot_width, slot_length)

part = result
part.name = "knob_with_tab"
export_step(part, "output.step")
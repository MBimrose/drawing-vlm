from build123d import *

width = 40.0
height = 30.0
thickness = 8.0
tab_width = 12.0
tab_height = 20.0
slot_width = 12.0
slot_height = 20.0
hole_diameter = 6.0
fillet_radius = 2.0
chamfer_distance = 0.8

base = Box(width, height, thickness)
tab = Pos(width/2 + tab_width/2, 0, 0) * Box(tab_width, tab_height, thickness)
result = base + tab

slot = Pos(-width/2 - slot_width/2, 0, 0) * Box(slot_width, slot_height, thickness)
result = result - slot

hole = Pos(width/2 + tab_width, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, thickness + 1)
result = result - hole

right_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
result = fillet(right_edges, fillet_radius)

left_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
result = chamfer(left_edges, chamfer_distance)

part = result
part.name = "bracket_with_tab_and_slot"
export_step(part, "output.step")
from build123d import *

knob_length = 40.0
knob_width = 30.0
knob_thickness = 8.0
wall_thickness = 0.6
tab_width = 12.0
tab_height = 20.0
fillet_radius = 2.0
chamfer_distance = 0.8
pocket_length = 20.0
pocket_width = 10.0
pocket_depth = 2.0
blind_hole_diameter = 6.0
blind_hole_depth = 4.5

base = Box(knob_length, knob_width, knob_thickness)
tab = Pos(knob_length/2 + tab_width/2, 0, 0) * Box(tab_width, tab_height, knob_thickness)
result = base + tab

pocket = Pos(0, 0, knob_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

hole = Pos(knob_length/2 + tab_width - blind_hole_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
result = result - hole

fillet_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
result = fillet(fillet_edges, fillet_radius)

chamfer_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
result = chamfer(chamfer_edges, chamfer_distance)

part = result
part.name = "knob_with_tab"
export_step(part, "output.step")
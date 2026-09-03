from build123d import *

body_width = 40.0
body_height = 30.0
body_thickness = 8.0
tab_width = 12.0
tab_height = 20.0
tab_fillet = 2.0
hole_diameter = 6.0
hole_depth = 5.0
chamfer_size = 0.8

base = Box(body_width, body_height, body_thickness)
tab = Pos(body_width/2 + tab_width/2, 0, 0) * Box(tab_width, tab_height, body_thickness)
result = base + tab

tab_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
result = fillet(tab_edges, tab_fillet)

hole_center_x = body_width/2 + tab_width - hole_depth/2
hole = Pos(hole_center_x, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
result = result - hole

chamfer_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
result = chamfer(chamfer_edges, chamfer_size)

part = result
part.name = "body_with_tab"
export_step(part, "output.step")
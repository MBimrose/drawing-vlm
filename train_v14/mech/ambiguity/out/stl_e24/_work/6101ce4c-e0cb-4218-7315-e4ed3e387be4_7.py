from build123d import *

body_width = 40.0
body_depth = 30.0
body_thickness = 8.0
tab_length = 12.0
tab_width = 20.0
tab_fillet_radius = 2.0
hole_diameter = 6.0
hole_depth = 5.0
edge_chamfer = 0.8

body = Box(body_width, body_depth, body_thickness)
tab = Pos(body_width/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, body_thickness)
result = body + tab

tab_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
result = fillet(tab_edges, tab_fillet_radius)

hole = Pos(body_width/2 + tab_length - hole_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
result = result - hole

chamfer_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
result = chamfer(chamfer_edges, edge_chamfer)

part = result
part.name = "body_with_tab"
export_step(part, "output.step")
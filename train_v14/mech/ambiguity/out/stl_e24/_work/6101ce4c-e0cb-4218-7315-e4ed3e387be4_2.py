from build123d import *

body_width = 40.0
body_height = 30.0
thickness = 8.0
tab_width = 12.0
tab_height = 20.0
tab_fillet_radius = 2.0
hole_diameter = 6.0
chamfer_distance = 0.8
rib_width = 6.0
rib_height = 12.0
rib_thickness = 4.0

base = Box(body_width, body_height, thickness)
tab = Pos(body_width/2 + tab_width/2, 0, 0) * Box(tab_width, tab_height, thickness)
result = base + tab

hole = Pos(body_width/2 + tab_width, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, thickness + 1)
result = result - hole

fillet_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
result = fillet(fillet_edges, tab_fillet_radius)

rib = Pos(-body_width/2 + rib_width/2, 0, 0) * Box(rib_width, rib_height, rib_thickness)
result = result + rib

chamfer_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
result = chamfer(chamfer_edges, chamfer_distance)

part = result
part.name = "body_with_tab_rib"
export_step(part, "output.step")
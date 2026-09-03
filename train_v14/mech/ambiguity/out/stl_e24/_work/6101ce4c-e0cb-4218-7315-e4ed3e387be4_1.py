from build123d import *

base_length = 40.0
base_width = 30.0
base_thickness = 8.0
tab_length = 12.0
tab_width = 20.0
fillet_radius = 2.0
chamfer_distance = 0.8
hole_diameter = 6.0
hole_depth = 4.5

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
tab = Pos(base_length/2 + tab_length/2, 0, base_thickness/2) * Box(tab_length, tab_width, base_thickness)
result = base + tab

fillet_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
result = fillet(fillet_edges, fillet_radius)

chamfer_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
result = chamfer(chamfer_edges, chamfer_distance)

hole = Pos(base_length/2 + tab_length - hole_depth/2, 0, base_thickness/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
result = result - hole

part = result
part.name = "base_with_tab"
export_step(part, "output.step")
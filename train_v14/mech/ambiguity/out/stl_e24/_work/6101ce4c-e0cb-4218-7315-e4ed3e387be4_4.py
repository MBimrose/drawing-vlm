from build123d import *

plate_width = 40.0
plate_height = 30.0
plate_thickness = 8.0
tab_width = 12.0
tab_height = 20.0
tab_fillet_radius = 2.0
blind_hole_diameter = 6.0
blind_hole_depth = 4.5
edge_chamfer = 0.8

base = Box(plate_width, plate_height, plate_thickness)
tab = Pos(plate_width/2 + tab_width/2, 0, 0) * Box(tab_width, tab_height, plate_thickness)
result = base + tab

hole = Pos(plate_width/2 + tab_width - blind_hole_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
result = result - hole

fillet_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
result = fillet(fillet_edges, tab_fillet_radius)

chamfer_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
result = chamfer(chamfer_edges, edge_chamfer)

part = result
part.name = "plate_with_tab"
export_step(part, "output.step")
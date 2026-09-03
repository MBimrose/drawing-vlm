from build123d import *

plate_width = 80.0
plate_depth = 40.0
plate_thickness = 4.0
tab_width = 20.0
tab_height = 8.0
pocket_width = 30.0
pocket_depth = 15.0
pocket_cut_depth = 2.0
hole_diameter = 4.0
hole_spacing = 25.0
chamfer_size = 0.5
fillet_radius = 0.5
rib_height = 1.0
rib_width = 10.0
rib_depth = 20.0

base = Box(plate_width, plate_depth, plate_thickness)
tab = Pos(0, plate_depth/2 + tab_height/2, 0) * Box(plate_width, tab_height, plate_thickness)
result = base + tab

pocket = Pos(0, 0, plate_thickness/2 - pocket_cut_depth/2) * Box(pocket_width, pocket_depth, pocket_cut_depth)
result = result - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, rib_depth, rib_height)
result = result + rib

tab_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:]
result = chamfer(tab_edges, chamfer_size)

fillet_edges = result.edges().filter_by(Axis.Z)
result = fillet(fillet_edges, fillet_radius)

part = result
part.name = "plate_with_tab_pocket_holes_rib"
export_step(part, "output.step")
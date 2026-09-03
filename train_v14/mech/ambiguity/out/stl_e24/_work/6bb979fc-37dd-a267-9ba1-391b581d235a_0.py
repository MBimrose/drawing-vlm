from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_height = 5.0
rib_thickness = 2.0
rib_width = 10.0
tab_width = 12.0
tab_height = 6.0
tab_thickness = 3.0
pocket_width = 10.0
pocket_height = 4.0
pocket_depth = 1.0
hole_diameter = 5.0
hole_spacing = 20.0
chamfer_size = 0.5

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

rib = Pos(0, -outer_width/2 - rib_thickness/2, outer_height/2 - rib_height/2) * Box(rib_thickness, rib_width, rib_height)
base = base + rib

tab = Pos(0, outer_width/2 + tab_thickness/2, outer_height/2 - tab_height/2) * Box(tab_width, tab_thickness, tab_height)
base = base + tab

pocket = Pos(0, outer_width/2 + tab_thickness - pocket_depth/2, outer_height/2 - tab_height/2) * Box(pocket_width, pocket_depth, pocket_height)
base = base - pocket

for x in [-hole_spacing, 0, hole_spacing]:
    base = base - Pos(x, 0, outer_height/2) * Cylinder(hole_diameter/2, outer_height + 10)

top_edges = base.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
base = chamfer(top_edges, chamfer_size)

part = base
part.name = "hollow_box_with_rib_tab"
export_step(part, "output.step")
from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 10.0
tab_width = 12.0
tab_height = 8.0
tab_overlap = 2.0
pocket_width = 6.0
pocket_depth = 4.0
notch_width = 10.0
notch_height = 5.0
notch_offset = 20.0

outer_radius = outer_diameter / 2.0

base = Cylinder(outer_radius, thickness)
tab = Pos(outer_radius + tab_width/2.0 - tab_overlap, 0, 0) * Box(tab_width, tab_height, thickness)
result = base + tab

result = result - Cylinder(inner_diameter/2, thickness)

pocket = Pos(outer_radius + tab_width/2.0 - tab_overlap, 0, thickness/2.0 - pocket_depth/2.0) * Box(pocket_width, tab_height, pocket_depth)
result = result - pocket

notch = Pos(outer_radius - notch_width/2.0, notch_offset, 0) * Box(notch_width, notch_height, thickness)
result = result - notch

part = result
part.name = "disc_with_tab"
export_step(part, "output.step")
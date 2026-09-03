from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 10.0
tab_width = 20.0
tab_height = 10.0
tab_thickness = 8.0
tab_overlap = 2.0
pocket_width = 12.0
pocket_height = 6.0
pocket_depth = 4.0
hole_diameter = 4.0
hole_spacing = 12.0
chamfer_size = 1.0
rib_width = 4.0
rib_height = 6.0
rib_thickness = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, thickness) - Cylinder(inner_radius, thickness)

tab_center_x = outer_radius + tab_thickness / 2.0 - tab_overlap
result = result + Pos(tab_center_x, 0, 0) * Box(tab_width, tab_thickness, tab_height)

pocket_center_x = tab_center_x + tab_width / 2.0 - pocket_depth / 2.0
result = result - Pos(pocket_center_x, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)

for y in [-hole_spacing / 2.0, hole_spacing / 2.0]:
    result = result - Pos(tab_center_x, y, 0) * Cylinder(hole_diameter / 2.0, tab_height)

rib_center_x = tab_center_x - tab_width / 2.0 + rib_thickness / 2.0
result = result + Pos(rib_center_x, 0, 0) * Box(rib_thickness, rib_width, rib_height)

part = result
part.name = "flanged_disc_with_tab"
export_step(part, "output.step")
from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 20.0
tab_width = 20.0
tab_height = 10.0
tab_thickness = 6.0
chamfer_size = 1.0
mount_hole_diameter = 8.0
mount_hole_spacing = 30.0
pocket_width = 25.0
pocket_depth = 12.0
pocket_height = 5.0

base = Cylinder(outer_diameter / 2, thickness)
tab = Pos(0, outer_diameter / 2 + tab_thickness / 2, 0) * Box(tab_width, tab_thickness, thickness)
result = base + tab

result = result - Cylinder(inner_diameter / 2, thickness)

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter / 2, thickness)

pocket = Pos(0, 0, thickness - pocket_height / 2) * Box(pocket_width, pocket_depth, pocket_height)
result = result - pocket

part = result
part.name = "flanged_disc_with_tab"
export_step(part, "output.step")
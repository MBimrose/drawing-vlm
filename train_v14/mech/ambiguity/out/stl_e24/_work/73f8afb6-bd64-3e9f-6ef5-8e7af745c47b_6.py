from build123d import *

outer_diameter = 80.0
wall_thickness = 5.0
cap_height = 30.0
groove_width = 8.0
groove_depth = 2.0
groove_position = 10.0
chamfer_size = 0.8
tab_width = 20.0
tab_height = 10.0
tab_thickness = wall_thickness
mount_hole_diameter = 5.0
mount_hole_spacing = 14.0
pocket_width = 30.0
pocket_depth = 12.0
pocket_height = 8.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

result = Cylinder(outer_radius, cap_height) - Cylinder(inner_radius, cap_height)
result = chamfer(result.edges(), chamfer_size)

groove = Cylinder(inner_radius, groove_width) - Cylinder(inner_radius - groove_depth, groove_width)
groove = Pos(0, 0, groove_position - cap_height / 2) * groove
result = result - groove

tab = Pos(outer_radius + tab_thickness / 2 - 0.5, 0, 0) * Box(tab_thickness, tab_width, tab_height)
result = result + tab

for y in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    hole = Pos(outer_radius + tab_thickness / 2, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, 100)
    result = result - hole

pocket = Pos(-outer_radius + pocket_height / 2, 0, 0) * Box(pocket_height, pocket_width, pocket_depth)
result = result - pocket

part = result
part.name = "cap_with_groove_tab_pocket"
export_step(part, "output.step")
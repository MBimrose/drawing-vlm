from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
height = 20.0
split_width = 5.0
tab_width = 20.0
tab_height = 12.0
mount_hole_dia = 8.0
mount_hole_spacing = 30.0
chamfer_dist = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
tab_center_y = outer_radius + tab_height / 2.0

solid_body = Cylinder(outer_radius, height)
solid_body = solid_body + Pos(0, tab_center_y, 0) * Box(tab_width, tab_height, height)
solid_body = solid_body - Cylinder(inner_radius, height)
solid_body = solid_body - Pos(outer_radius - split_width / 2.0, 0, 0) * Box(split_width, height, height)

for x in [-mount_hole_spacing / 2.0, mount_hole_spacing / 2.0]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_dia / 2.0, height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_dist)

part = solid_body
part.name = "split_ring_with_tab"
export_step(part, "output.step")
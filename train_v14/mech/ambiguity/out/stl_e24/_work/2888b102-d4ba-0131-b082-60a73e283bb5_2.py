from build123d import *

overall_length = 80.0
overall_width = 40.0
overall_thickness = 12.0
wall_thickness = 4.0
tab_length = 20.0
tab_width = 8.0
blind_hole_diameter = 6.0
blind_hole_depth = 8.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
chamfer_size = 1.0

base = Box(overall_length, overall_width, overall_thickness)
tab = Pos(overall_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, overall_thickness)
solid_body = base + tab

inner_length = overall_length - 2 * wall_thickness
inner_width = overall_width - 2 * wall_thickness
pocket = Box(inner_length, inner_width, overall_thickness)
solid_body = solid_body - pocket

blind_hole = Pos(0, 0, overall_thickness/2 - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - blind_hole

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    mount_hole = Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, overall_thickness)
    solid_body = solid_body - mount_hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "box_with_tab_and_holes"
export_step(part, "output.step")
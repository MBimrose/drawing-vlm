from build123d import *

overall_width = 80.0
overall_height = 50.0
overall_depth = 20.0
wall_thickness = 3.0
corner_radius = 5.0
mount_hole_dia = 5.0
mount_hole_spacing = 30.0
pocket_width = 40.0
pocket_depth = 30.0
pocket_height = 8.0

solid = Box(overall_width, overall_height, overall_depth)
solid = fillet(solid.edges().filter_by(Axis.Z), corner_radius)

inner_w = overall_width - 2 * wall_thickness
inner_h = overall_height - 2 * wall_thickness
solid = solid - Box(inner_w, inner_h, overall_depth)

hole_r = mount_hole_dia / 2
hole_h = overall_depth + 1
for x in [-overall_width/2, overall_width/2]:
    for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
        solid = solid - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

pocket_z = overall_depth/2 - pocket_height/2
solid = solid - Pos(0, 0, pocket_z) * Box(pocket_width, pocket_depth, pocket_height)

part = solid
part.name = "hollow_box_with_holes_and_pocket"
export_step(part, "output.step")
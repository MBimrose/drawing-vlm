from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 5.0
rear_chamfer = 1.5
mount_hole_dia = 3.0
mount_hole_spacing_x = 50.0
mount_hole_spacing_y = 40.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, outer_width/2 - pocket_depth/2, outer_height/2 - pocket_width/2) * Box(pocket_length, pocket_depth, pocket_width)
solid_body = solid_body - pocket

rear_face = solid_body.faces().sort_by(Axis.Y)[0]
rear_vertical_edges = rear_face.edges().filter_by(Axis.Z)
solid_body = chamfer(rear_vertical_edges, rear_chamfer)

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    hole = Pos(x, y, outer_height/2) * Cylinder(mount_hole_dia/2, outer_height)
    solid_body = solid_body - hole

part = solid_body
part.name = "shelled_box_with_pocket"
export_step(part, "output.step")
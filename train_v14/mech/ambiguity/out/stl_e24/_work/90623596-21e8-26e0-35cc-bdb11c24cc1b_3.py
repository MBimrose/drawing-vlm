from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 10.0
chamfer_size = 0.5
mount_hole_diameter = 4.0
mount_hole_spacing = 20.0
mount_hole_offset = 10.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket_box = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket_box

hole_cyl = Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length)
solid_body = solid_body - Pos(outer_length/2, 0, outer_height/2) * hole_cyl

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "shelled_box_with_pocket"
export_step(part, "output.step")
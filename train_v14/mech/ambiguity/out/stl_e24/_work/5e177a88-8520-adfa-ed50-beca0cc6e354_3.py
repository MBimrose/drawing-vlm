from build123d import *

outer_width = 80.0
outer_depth = 80.0
outer_height = 30.0
wall_thickness = 4.0
pocket_radius = 20.0
pocket_depth = 12.0
chamfer_size = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 30.0

solid_body = Box(outer_width, outer_depth, outer_height)

pocket = Pos(0, 0, outer_height/2 - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)
solid_body = solid_body - pocket

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_size)

hole = Pos(mount_hole_offset, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, outer_depth)
solid_body = solid_body - hole

part = solid_body
part.name = "XMountSocket"
export_step(part, "output.step")
from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = 20.0
rib_length = 60.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 12.0
mount_hole_dia = 4.0
mount_hole_offset = 10.0
chamfer_size = 1.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

rib = Pos(outer_length/2 - wall_thickness - rib_thickness/2, 0, rib_height/2) * Box(rib_thickness, rib_length, rib_height)
solid_body = solid_body + rib

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole_positions = [
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
    (-outer_length/2 + mount_hole_offset,  outer_width/2 - mount_hole_offset),
    ( outer_length/2 - mount_hole_offset,  outer_width/2 - mount_hole_offset)
]
for x, y in hole_positions:
    hole = Pos(x, y, outer_height/2) * Cylinder(mount_hole_dia/2, outer_height)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_enclosure_with_rib"
export_step(part, "output.step")
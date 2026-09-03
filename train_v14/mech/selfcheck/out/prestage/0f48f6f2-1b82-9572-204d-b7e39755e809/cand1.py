from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 3.0
rib_width = 30.0
rib_height = 10.0
rib_length = outer_length - 2 * wall_thickness
pocket_length = 40.0
pocket_width = 20.0
pocket_depth = 8.0
chamfer_distance = 2.0
mount_hole_dia = 5.0
mount_hole_spacing = 60.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

pocket = Pos(0, 0, outer_height - wall_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for x, y in [(-mount_hole_spacing/2, 0), (mount_hole_spacing/2, 0)]:
    hole = Pos(x, y, outer_height/2) * Cylinder(mount_hole_dia/2, outer_height)
    solid_body = solid_body - hole

front_face = solid_body.faces().sort_by(Axis.X)[-1]
front_edges = front_face.edges()
solid_body = chamfer(front_edges, chamfer_distance)

part = solid_body
part.name = "shelled_box_with_rib_pocket"
export_step(part, "output.step")
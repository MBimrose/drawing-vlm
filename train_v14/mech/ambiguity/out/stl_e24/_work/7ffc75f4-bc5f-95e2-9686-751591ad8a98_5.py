from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
front_open_width = 30.0
front_open_height = 10.0
mount_hole_diameter = 2.0
mount_hole_offset = 5.0
fillet_radius = 1.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

front_cut = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(front_open_width, wall_thickness, front_open_height)
solid_body = solid_body - front_cut

px = outer_length/2 - mount_hole_offset
py = outer_width/2 - mount_hole_offset
for x, y in [(px, py), (-px, py), (-px, -py), (px, -py)]:
    solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)

part = solid_body
part.name = "shelled_box_with_openings"
export_step(part, "output.step")
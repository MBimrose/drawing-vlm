from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
corner_fillet = 0.5
top_chamfer = 0.8
opening_width = 10.0
opening_height = 5.0
mount_hole_dia = 2.0
mount_hole_spacing = 30.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, top_chamfer)

inner = offset(solid_body, amount=-wall_thickness)
solid_body = solid_body - inner

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, corner_fillet)

opening = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(opening_width, wall_thickness, opening_height)
solid_body = solid_body - opening

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(0, y, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, outer_length)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_box_with_opening"
export_step(part, "output.step")
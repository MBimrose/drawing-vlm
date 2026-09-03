from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 3.0
cavity_length = 40.0
cavity_width = 30.0
cavity_depth = outer_height - wall_thickness - 5.0
chamfer_distance = 2.0
mount_hole_dia = 4.0
mount_hole_spacing = 30.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

cavity = Pos(0, 0, outer_height - cavity_depth/2) * Box(cavity_length, cavity_width, cavity_depth)
solid_body = solid_body - cavity

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

hole = Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, outer_length + 20)
for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(outer_length/2, y, outer_height/2) * hole
    solid_body = solid_body - Pos(-outer_length/2, y, outer_height/2) * hole

part = solid_body
part.name = "shelled_box_with_cavity_and_mount_holes"
export_step(part, "output.step")
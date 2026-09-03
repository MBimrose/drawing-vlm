from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
base_thickness = 3.0
chamfer_distance = 0.5
mount_hole_diameter = 2.0
mount_hole_offset = 5.0
opening_length = 40.0
opening_width = 30.0

total_height = outer_height + base_thickness

solid_body = Pos(0, 0, total_height / 2) * Box(outer_length, outer_width, total_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

opening = Pos(0, 0, total_height - wall_thickness / 2) * Box(opening_length, opening_width, wall_thickness)
solid_body = solid_body - opening

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_distance)

hole_r = mount_hole_diameter / 2
hole_h = total_height + 10
for x in [-outer_length / 2 + mount_hole_offset, outer_length / 2 - mount_hole_offset]:
    for y in [-outer_width / 2 + mount_hole_offset, outer_width / 2 - mount_hole_offset]:
        solid_body = solid_body - Pos(x, y, total_height / 2) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "hollow_box_with_opening"
export_step(part, "output.step")
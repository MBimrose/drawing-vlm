from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_width = 5.0
rib_height = 5.0
chamfer_size = 0.5
mount_hole_dia = 3.0
mount_hole_offset = 4.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness

base = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

rib_z = outer_height + rib_height / 2
rib1 = Pos(-outer_length/2 + rib_width/2, -outer_width/2 + rib_width/2, rib_z) * Box(rib_width, rib_width, rib_height)
rib2 = Pos(outer_length/2 - rib_width/2, -outer_width/2 + rib_width/2, rib_z) * Box(rib_width, rib_width, rib_height)
rib3 = Pos(-outer_length/2 + rib_width/2, outer_width/2 - rib_width/2, rib_z) * Box(rib_width, rib_width, rib_height)
rib4 = Pos(outer_length/2 - rib_width/2, outer_width/2 - rib_width/2, rib_z) * Box(rib_width, rib_width, rib_height)
base = base + rib1 + rib2 + rib3 + rib4

vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_size)

hole_r = mount_hole_dia / 2
hole_h = outer_height + 20
hole_z = mount_hole_offset
hole_x = outer_length / 2
hole_y = outer_width / 2

hole_x_pos = Pos(hole_x, 0, hole_z) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
hole_x_neg = Pos(-hole_x, 0, hole_z) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
hole_y_pos = Pos(0, hole_y, hole_z) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)
hole_y_neg = Pos(0, -hole_y, hole_z) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)

base = base - hole_x_pos - hole_x_neg - hole_y_pos - hole_y_neg

part = base
part.name = "shelled_box_with_ribs_and_holes"
export_step(part, "output.step")
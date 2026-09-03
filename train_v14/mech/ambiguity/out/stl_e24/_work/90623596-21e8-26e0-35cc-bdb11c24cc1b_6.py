from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
pocket_depth = 12.0
pocket_margin = 5.0
slot_width = 4.0
slot_length = 30.0
slot_depth = 6.0
mount_hole_dia = 4.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket_w = outer_length - 2 * pocket_margin
pocket_h = outer_width - 2 * pocket_margin
pocket_box = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)
solid_body = solid_body - pocket_box

slot_box = Pos(0, 0, outer_height - slot_depth/2) * Box(slot_length, slot_width, slot_depth)
solid_body = solid_body - slot_box

hole = Pos(outer_length/2, 0, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, outer_length)
solid_body = solid_body - hole

part = solid_body
part.name = "shelled_box_with_pocket_slot_hole"
export_step(part, "output.step")
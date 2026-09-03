from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
front_chamfer = 0.8
bottom_fillet = 0.5
slot_width = 12.0
slot_height = 5.0
mount_hole_dia = 2.0
mount_hole_spacing = 30.0
mount_hole_offset = 15.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

inner = offset(solid_body, amount=-wall_thickness)
solid_body = solid_body - inner

front_face = solid_body.faces().sort_by(Axis.Y)[-1]
front_vertical_edges = front_face.edges().filter_by(Axis.Z)
solid_body = chamfer(front_vertical_edges, front_chamfer)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = fillet(bottom_edges, bottom_fillet)

slot = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(slot_width, wall_thickness, slot_height)
solid_body = solid_body - slot

for y_pos in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(0, y_pos, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, outer_length)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_box_with_slot_and_holes"
export_step(part, "output.step")
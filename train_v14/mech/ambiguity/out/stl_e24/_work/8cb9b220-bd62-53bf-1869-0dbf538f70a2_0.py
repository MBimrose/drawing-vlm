from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
slot_width = 12.0
slot_height = 5.0
mount_hole_dia = 2.0
mount_hole_spacing = 30.0
chamfer_size = 0.8
fillet_radius = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
inner_box = Pos(0, 0, outer_height/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, outer_height - 2*wall_thickness)
solid_body = solid_body - inner_box

slot_cut = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(slot_width, wall_thickness, slot_height)
solid_body = solid_body - slot_cut

for y_pos in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(0, y_pos, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, outer_length)
    solid_body = solid_body - hole

top_x_edges = solid_body.edges().filter_by(Axis.X).sort_by(Axis.Z)[-2:]
solid_body = chamfer(top_x_edges, chamfer_size)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "hollow_enclosure_with_slot_and_mount_holes"
export_step(part, "output.step")
from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
slot_width = 15.0
slot_height = 10.0
rear_chamfer = 1.5
mount_hole_dia = 3.0
mount_hole_spacing_x = 50.0
mount_hole_spacing_y = 40.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_box = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(slot_width, wall_thickness, slot_height)
solid_body = solid_body - slot_box

rear_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Y)[:2]
solid_body = chamfer(rear_edges, rear_chamfer)

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(mount_hole_dia/2, outer_height)

part = solid_body
part.name = "shelled_box_with_slot_and_mount_holes"
export_step(part, "output.step")
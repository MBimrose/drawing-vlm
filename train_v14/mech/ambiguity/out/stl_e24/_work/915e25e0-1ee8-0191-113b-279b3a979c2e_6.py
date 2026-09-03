from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
vent_slot_width = 4.0
vent_slot_height = 8.0
vent_spacing_x = 12.0
vent_spacing_y = 12.0
vent_rows = 2
vent_cols = 3
mount_tab_width = 20.0
mount_tab_height = 12.0
mount_tab_thickness = 5.0
mount_hole_diameter = 3.0
mount_hole_spacing_x = 60.0
mount_hole_spacing_y = 8.0
chamfer_distance = 1.0
internal_pocket_depth = 6.0
internal_pocket_margin = 10.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

for i in range(vent_cols):
    for j in range(vent_rows):
        y_pos = (i - (vent_cols-1)/2) * vent_spacing_x
        z_pos = outer_height/2 + (j - (vent_rows-1)/2) * vent_spacing_y
        vent = Pos(outer_length/2 - wall_thickness/2, y_pos, z_pos) * Box(wall_thickness, vent_slot_width, vent_slot_height)
        solid_body = solid_body - vent

tab = Pos(0, outer_width/2 + mount_tab_thickness/2, outer_height/2) * Box(mount_tab_width, mount_tab_thickness, mount_tab_height)
solid_body = solid_body + tab

for i in range(2):
    for j in range(2):
        x_pos = (i - 0.5) * mount_hole_spacing_x
        z_pos = outer_height/2 + (j - 0.5) * mount_hole_spacing_y
        hole = Pos(x_pos, 0, z_pos) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, outer_width + mount_tab_thickness + 10)
        solid_body = solid_body - hole

front_face = solid_body.faces().sort_by(Axis.Y)[0]
solid_body = chamfer(front_face.edges(), chamfer_distance)

rear_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = fillet(rear_face.edges(), 2.0)

pocket_w = outer_length - 2 * internal_pocket_margin
pocket_h = outer_width - 2 * internal_pocket_margin
pocket = Pos(0, 0, internal_pocket_depth/2) * Box(pocket_w, pocket_h, internal_pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")
from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
vent_slot_width = 4.0
vent_slot_height = 8.0
vent_slot_spacing = 12.0
vent_slot_count = 6
mount_tab_width = 20.0
mount_tab_height = 10.0
mount_tab_thickness = 5.0
mount_hole_diameter = 3.0
mount_hole_spacing = 12.0
chamfer_distance = 1.0
fillet_radius = 2.0
pocket_width = 30.0
pocket_height = 10.0
pocket_depth = 4.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

front_face = solid_body.faces().sort_by(Axis.Y)[0]
solid_body = chamfer(front_face.edges(), chamfer_distance)

for i in range(vent_slot_count):
    y_pos = (i - (vent_slot_count - 1) / 2) * vent_slot_spacing
    slot = Pos(outer_length/2 - wall_thickness/2, y_pos, outer_height/2) * Box(wall_thickness, vent_slot_width, vent_slot_height)
    solid_body = solid_body - slot

tab = Pos(0, outer_width/2 + mount_tab_thickness/2, outer_height/2) * Box(mount_tab_width, mount_tab_thickness, mount_tab_height)
solid_body = solid_body + tab

for x in [-outer_length/2 + mount_hole_spacing/2, outer_length/2 - mount_hole_spacing/2]:
    for z in [outer_height/2 - mount_hole_spacing/2, outer_height/2 + mount_hole_spacing/2]:
        hole = Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, outer_width + mount_tab_thickness + 10)
        solid_body = solid_body - hole

pocket = Pos(outer_length/2 - pocket_depth/2, 0, outer_height/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

back_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = fillet(back_face.edges(), fillet_radius)

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")
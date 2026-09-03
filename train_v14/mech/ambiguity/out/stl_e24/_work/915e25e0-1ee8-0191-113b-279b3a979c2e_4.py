from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
vent_slot_width = 4.0
vent_slot_height = 8.0
vent_spacing = 12.0
vent_rows = 2
vent_columns = 4
mount_tab_width = 20.0
mount_tab_height = 10.0
mount_tab_thickness = 5.0
mount_hole_diameter = 3.0
mount_hole_offset_x = 8.0
mount_hole_offset_y = 4.0
chamfer_size = 1.0
fillet_radius = 2.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

for i in range(vent_columns):
    for j in range(vent_rows):
        y_pos = (i - (vent_columns - 1) / 2) * vent_spacing
        z_pos = outer_height/2 + (j - (vent_rows - 1) / 2) * vent_spacing
        vent = Pos(outer_length/2 - wall_thickness/2, y_pos, z_pos) * Box(wall_thickness, vent_slot_width, vent_slot_height)
        solid_body = solid_body - vent

tab = Pos(0, outer_width/2 + mount_tab_thickness/2, outer_height/2) * Box(mount_tab_width, mount_tab_thickness, mount_tab_height)
solid_body = solid_body + tab

hole_positions = [
    (-outer_length/2 + mount_hole_offset_x, -outer_height/2 + mount_hole_offset_y),
    (outer_length/2 - mount_hole_offset_x, -outer_height/2 + mount_hole_offset_y),
    (-outer_length/2 + mount_hole_offset_x, outer_height/2 - mount_hole_offset_y),
    (outer_length/2 - mount_hole_offset_x, outer_height/2 - mount_hole_offset_y),
]
for x, z in hole_positions:
    hole = Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, outer_width + mount_tab_thickness + 10)
    solid_body = solid_body - hole

rear_face = solid_body.faces().sort_by(Axis.Y)[0]
solid_body = chamfer(rear_face.edges(), chamfer_size)

front_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = fillet(front_face.edges(), fillet_radius)

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")
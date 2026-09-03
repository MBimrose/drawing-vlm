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
mount_hole_diameter = 3.0
mount_hole_offset = 8.0
tab_length = 20.0
tab_height = 12.0
tab_thickness = 5.0
chamfer_distance = 1.0
fillet_radius = 2.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

front_face = solid_body.faces().sort_by(Axis.Y)[0]
solid_body = chamfer(front_face.edges(), chamfer_distance)

for i in range(vent_cols):
    for j in range(vent_rows):
        y_pos = (i - (vent_cols-1)/2) * vent_spacing_x
        z_pos = outer_height/2 + (j - (vent_rows-1)/2) * vent_spacing_y
        slot = Pos(outer_length/2 - wall_thickness/2, y_pos, z_pos) * Box(wall_thickness, vent_slot_width, vent_slot_height)
        solid_body = solid_body - slot

hole_positions = [
    (-outer_length/2 + mount_hole_offset, -outer_height/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset, -outer_height/2 + mount_hole_offset),
    (-outer_length/2 + mount_hole_offset,  outer_height/2 - mount_hole_offset),
    ( outer_length/2 - mount_hole_offset,  outer_height/2 - mount_hole_offset)
]
for x, z in hole_positions:
    hole = Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, outer_width + 10)
    solid_body = solid_body - hole

tab = Pos(0, outer_width/2 + tab_thickness/2, outer_height/2) * Box(tab_length, tab_thickness, tab_height)
solid_body = solid_body + tab

rear_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = fillet(rear_face.edges(), fillet_radius)

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")
from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_width = 12.0
vent_slot_height = 5.0
vent_spacing = 15.0
rear_vent_slot_width = 1.0
rear_vent_slot_height = 6.0
rear_vent_spacing = 8.0
rear_vent_rows = 2
rear_vent_cols = 10
chamfer_size = 1.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

vent1 = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2) * Box(vent_slot_width, wall_thickness, vent_slot_height)
vent2 = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2 - vent_spacing) * Box(vent_slot_width, wall_thickness, vent_slot_height)
solid_body = solid_body - vent1 - vent2

for row in range(rear_vent_rows):
    y_offset = (row - (rear_vent_rows - 1) / 2) * rear_vent_spacing
    for col in range(rear_vent_cols):
        x_offset = (col - (rear_vent_cols - 1) / 2) * rear_vent_spacing
        slot = Pos(x_offset, -outer_width/2 + wall_thickness/2, outer_height/2 + y_offset) * Box(rear_vent_slot_width, wall_thickness, rear_vent_slot_height)
        solid_body = solid_body - slot

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")
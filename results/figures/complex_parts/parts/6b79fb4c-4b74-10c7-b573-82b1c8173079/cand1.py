from build123d import *

channel_length = 100.0
channel_width = 80.0
channel_height = 40.0
wall_thickness = 5.0
slot_width = 2.0
slot_length = 60.0
slot_spacing = 15.0
num_slots = 3
chamfer_size = 2.0
hole_diameter = 8.0
hole_offset_y = 20.0
hole_offset_z = 0.0
vent_hole_dia = 3.0
vent_rows = 3
vent_cols = 4
vent_spacing_x = 12.0
vent_spacing_y = 12.0

solid_body = Box(channel_width, channel_length, channel_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

inner = Pos(wall_thickness/2, 0, 0) * Box(channel_width - wall_thickness, channel_length, channel_height - 2*wall_thickness)
solid_body = solid_body - inner

for i in range(num_slots):
    x_pos = (i - (num_slots-1)/2) * slot_spacing
    slot = Pos(x_pos, 0, channel_height/2 - wall_thickness/2) * Box(slot_length, channel_length, slot_width)
    solid_body = solid_body - slot

hole = Pos(-channel_width/2, hole_offset_y, hole_offset_z) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, channel_width)
solid_body = solid_body - hole

for i in range(vent_cols):
    for j in range(vent_rows):
        y_pos = (i - (vent_cols-1)/2) * vent_spacing_x
        z_pos = (j - (vent_rows-1)/2) * vent_spacing_y
        vent = Pos(-channel_width/2, y_pos, z_pos) * Rot(0, 90, 0) * Cylinder(vent_hole_dia/2, channel_width)
        solid_body = solid_body - vent

part = solid_body
part.name = "channel_with_slots_and_holes"
export_step(part, "output.step")
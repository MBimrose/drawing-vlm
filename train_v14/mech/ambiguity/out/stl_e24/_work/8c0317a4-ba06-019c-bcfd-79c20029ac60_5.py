from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.5
fillet_radius = 1.2
rib_width = 6.0
rib_height = 4.0
rib_spacing = 15.0
slot_width = 20.0
slot_height = 10.0
slot_depth = 5.0

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

rib_count = int((channel_length - 2 * wall_thickness) // rib_spacing)
for i in range(rib_count):
    x_pos = -channel_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, wall_thickness) * Box(rib_width, rib_height, wall_thickness)
    solid_body = solid_body + rib

slot = Pos(0, 0, channel_height - slot_depth/2) * Box(slot_width, slot_height, slot_depth)
solid_body = solid_body - slot

part = solid_body
part.name = "channel_with_ribs_and_slot"
export_step(part, "output.step")
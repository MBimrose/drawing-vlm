from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 20.0
wall_thickness = 3.0
slot_width = 10.0
slot_depth = 30.0
chamfer_size = 1.0
hole_diameter = 5.0
hole_spacing = 15.0
rib_thickness = 2.0
rib_height = 10.0
rib_spacing = 12.0

solid_body = Pos(0, 0, channel_length/2) * Box(channel_width, channel_height, channel_length)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

slot_box = Pos(0, 0, slot_depth/2) * Box(slot_width, channel_height - 2*wall_thickness, slot_depth)
solid_body = solid_body - slot_box

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0), (2*hole_spacing, 0)]:
    hole = Pos(x, y, channel_length/2) * Cylinder(hole_diameter/2, channel_length)
    solid_body = solid_body - hole

num_ribs = int((channel_width - 2*wall_thickness) // rib_spacing)
for i in range(num_ribs):
    x_pos = -channel_width/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, channel_height/2) * Box(rib_thickness, rib_height, channel_height - 2*wall_thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "channel_with_ribs"
export_step(part, "output.step")
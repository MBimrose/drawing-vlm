from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.5
fillet_radius = 1.2
slot_width = 20.0
slot_height = 12.0
slot_depth = 5.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
rib_width = 6.0
rib_height = 4.0
rib_spacing = 15.0

outer = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
inner = Pos(0, 0, channel_height/2) * Box(channel_length - 2*wall_thickness, channel_width - 2*wall_thickness, channel_height)
solid_body = outer - inner

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

slot_box = Pos(channel_length/2 - slot_depth/2, 0, channel_height/2) * Box(slot_depth, slot_width, slot_height)
solid_body = solid_body - slot_box

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, channel_height/2) * Cylinder(mount_hole_diameter/2, channel_height)
    solid_body = solid_body - hole

rib_count = int((channel_length - 2*wall_thickness) // rib_spacing)
for i in range(rib_count):
    x = -channel_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x, 0, wall_thickness/2) * Box(rib_width, rib_height, wall_thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "channel_with_ribs"
export_step(part, "output.step")
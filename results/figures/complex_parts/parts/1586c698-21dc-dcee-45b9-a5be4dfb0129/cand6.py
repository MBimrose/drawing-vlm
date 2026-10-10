from build123d import *

channel_length = 90.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 2.0
rib_width = 10.0
rib_height = 12.0
chamfer_size = 1.0
mount_hole_dia = 3.0
mount_hole_spacing = 40.0
internal_rib_thickness = 1.0
internal_rib_height = 12.0

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, channel_width/2 + rib_width/2, channel_height - rib_height/2) * Box(channel_length, rib_width, rib_height)
base = base + rib

chamfer_edges = base.edges().filter_by(Axis.X).sort_by(Axis.Z)[-2:]
base = chamfer(chamfer_edges, chamfer_size)

hole_r = mount_hole_dia / 2
hole_h = channel_height + 10
for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    base = base - Pos(x, 0, channel_height/2) * Cylinder(hole_r, hole_h)

int_rib = Pos(0, 0, internal_rib_height/2) * Box(internal_rib_thickness, channel_length, internal_rib_height)
base = base + int_rib

part = base
part.name = "channel_with_ribs"
export_step(part, "output.step")
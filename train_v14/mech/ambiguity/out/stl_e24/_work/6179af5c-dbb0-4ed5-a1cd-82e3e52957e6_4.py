from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 15.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = channel_height - 2 * wall_thickness
slot_width = 6.0
slot_depth = 4.0
chamfer_size = 0.5
hole_diameter = 3.0
hole_offset_from_end = 20.0

base = Box(channel_width, channel_height, channel_length)
top_face = base.faces().sort_by(Axis.Y)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib = Box(rib_thickness, rib_height, channel_length)
base = base + rib

slot = Pos(0, 0, channel_length/2 - slot_depth/2) * Box(slot_width, slot_depth, slot_depth)
base = base - slot

base = chamfer(base.edges(), chamfer_size)

hole1 = Pos(channel_width/2, 0, hole_offset_from_end) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, channel_length)
hole2 = Pos(-channel_width/2, 0, hole_offset_from_end) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, channel_length)
base = base - hole1 - hole2

part = base
part.name = "channel_with_rib"
export_step(part, "output.step")
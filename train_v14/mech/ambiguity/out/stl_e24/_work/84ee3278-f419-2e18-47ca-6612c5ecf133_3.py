from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.0
slot_width = 20.0
slot_height = channel_height - 2 * wall_thickness
hole_diameter = 6.0
hole_offset_from_end = 20.0
fillet_radius = 0.2

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

slot = Pos(0, 0, slot_height/2) * Box(channel_length, slot_width, slot_height)
base = base - slot

hole_x = -channel_length/2 + hole_offset_from_end
hole = Pos(hole_x, channel_width/2, channel_height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, channel_width)
base = base - hole

vertical_edges = base.edges().filter_by(Axis.Z)
base = fillet(vertical_edges, fillet_radius)

part = base
part.name = "channel_with_slot_and_hole"
export_step(part, "output.step")
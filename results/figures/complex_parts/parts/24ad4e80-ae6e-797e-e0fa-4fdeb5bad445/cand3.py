from build123d import *

channel_length = 100.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 3.0
slot_width = 10.0
slot_depth = 2.0
fillet_radius = 2.0
hole_diameter = 6.0
hole_offset_from_edge = 8.0

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
solid_body = fillet(solid_body.edges(), fillet_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_y = -channel_width/2 + wall_thickness + slot_width/2
slot_z = slot_depth/2
slot = Pos(0, slot_y, slot_z) * Box(channel_length - 2*wall_thickness, slot_width, slot_depth)
solid_body = solid_body - slot

hole_x = channel_length/2 - wall_thickness - hole_diameter/2
hole_y = -channel_width/2 + wall_thickness + hole_offset_from_edge
hole = Pos(hole_x, hole_y, channel_height/2) * Cylinder(hole_diameter/2, channel_height)
solid_body = solid_body - hole

part = solid_body
part.name = "channel_with_slot_and_hole"
export_step(part, "output.step")
from build123d import *

channel_length = 100.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 3.0
fillet_radius = 2.0
slot_length = 80.0
slot_width = 10.0
slot_offset_from_end = 10.0
hole_diameter = 6.0
hole_offset_from_end = 8.0
hole_offset_from_side = 8.0

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
solid_body = fillet(solid_body.edges(), fillet_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_center_x = -channel_length/2 + slot_offset_from_end + slot_length/2
slot_center_y = -channel_width/2 + wall_thickness + slot_width/2
slot_cut = Pos(slot_center_x, slot_center_y, channel_height/2) * Box(slot_length, slot_width, channel_height + 10)
solid_body = solid_body - slot_cut

hole_center_x = channel_length/2 - hole_offset_from_end
hole_center_y = -channel_width/2 + hole_offset_from_side
hole_cut = Pos(hole_center_x, hole_center_y, channel_height/2) * Cylinder(hole_diameter/2, channel_height + 10)
solid_body = solid_body - hole_cut

part = solid_body
part.name = "channel_with_slot_and_hole"
export_step(part, "output.step")
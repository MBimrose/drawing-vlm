from build123d import *

channel_length = 90.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 2.0
slot_width = 12.0
slot_height = 8.0
hole_diameter = 5.0
hole_offset = 20.0
rib_thickness = 1.0
rib_height = channel_height - 2 * wall_thickness

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

slot = Pos(0, 0, channel_height - wall_thickness/2) * Box(slot_width, slot_height, wall_thickness)
solid_body = solid_body - slot

for x in [-hole_offset, hole_offset]:
    hole = Pos(x, 0, channel_height/2) * Cylinder(hole_diameter/2, channel_height)
    solid_body = solid_body - hole

internal_rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(rib_thickness, channel_length, rib_height)
solid_body = solid_body + internal_rib

external_rib = Pos(0, channel_width/2 + rib_height/2, wall_thickness + rib_height/2) * Box(rib_thickness, rib_height, rib_height)
solid_body = solid_body + external_rib

part = solid_body
part.name = "channel_with_ribs"
export_step(part, "output.step")
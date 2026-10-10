from build123d import *

channel_length = 90.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 2.0
notch_width = 10.0
notch_depth = 5.0
notch_offset = 5.0
hole_diameter = 4.0
hole_spacing = 10.0
hole_offset_from_end = 15.0
rib_thickness = 1.0
rib_height = 10.0

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

notch_x = channel_length/2 - notch_offset - notch_width/2
notch_y = channel_width/2 - wall_thickness/2
notch_z = channel_height - notch_depth/2
solid_body = solid_body - Pos(notch_x, notch_y, notch_z) * Box(notch_width, wall_thickness, notch_depth)

hole_x = channel_length/2 - hole_offset_from_end
hole_y1 = channel_width/2 - wall_thickness/2
hole_y2 = channel_width/2 - wall_thickness/2 - hole_spacing
hole_z = channel_height/2
solid_body = solid_body - Pos(hole_x, hole_y1, hole_z) * Cylinder(hole_diameter/2, channel_height)
solid_body = solid_body - Pos(hole_x, hole_y2, hole_z) * Cylinder(hole_diameter/2, channel_height)

rib1 = Pos(0, 0, rib_height/2) * Box(channel_length, rib_thickness, rib_height)
rib2 = Pos(0, 0, rib_height/2) * Box(rib_thickness, channel_width, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "channel_with_notch_holes_and_ribs"
export_step(part, "output.step")
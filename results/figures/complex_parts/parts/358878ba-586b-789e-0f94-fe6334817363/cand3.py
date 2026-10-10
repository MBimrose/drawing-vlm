from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 40.0
wall_thickness = 2.0
slot_width = 30.0
slot_height = 10.0
hole_diameter = 5.0
hole_offset_from_end = 15.0
chamfer_distance = 0.5

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot = Pos(0, 0, channel_height - slot_height/2) * Box(slot_width, channel_width, slot_height)
solid_body = solid_body - slot

hole_x = channel_length/2 - hole_offset_from_end
hole = Pos(hole_x, 0, channel_height/2) * Cylinder(hole_diameter/2, channel_width)
solid_body = solid_body - hole

top_y_face = solid_body.faces().sort_by(Axis.Y)[-1]
top_y_edges = top_y_face.edges()
solid_body = chamfer(top_y_edges, chamfer_distance)

part = solid_body
part.name = "channel_with_slot_and_hole"
export_step(part, "output.step")
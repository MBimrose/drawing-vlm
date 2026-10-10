from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 40.0
wall_thickness = 2.0
slot_width = 30.0
slot_height = 10.0
hole_diameter = 5.0
hole_offset_x = 15.0
hole_offset_z = 10.0
chamfer_distance = 0.5

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_cut = Pos(0, 0, channel_height - slot_height/2) * Box(slot_width, channel_width + 10, slot_height)
solid_body = solid_body - slot_cut

hole1 = Pos(-hole_offset_x, 0, channel_height/2 + hole_offset_z) * Cylinder(hole_diameter/2, channel_width + 10)
hole2 = Pos(hole_offset_x, 0, channel_height/2 + hole_offset_z) * Cylinder(hole_diameter/2, channel_width + 10)
solid_body = solid_body - hole1 - hole2

front_face = solid_body.faces().sort_by(Axis.X)[-1]
front_edges = front_face.edges().filter_by(Axis.Y)
solid_body = chamfer(front_edges, chamfer_distance)

part = solid_body
part.name = "channel_with_slot_and_holes"
export_step(part, "output.step")
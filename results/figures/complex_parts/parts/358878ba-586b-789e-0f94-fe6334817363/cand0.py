from build123d import *

channel_length = 80.0
channel_width = 30.0
channel_height = 40.0
wall_thickness = 2.0
slot_width = 30.0
slot_height = 10.0
hole_diameter = 6.0
hole_spacing = 30.0
chamfer_size = 0.5

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_cut = Pos(0, 0, channel_height - slot_height/2) * Box(slot_width, channel_width + 10, slot_height)
solid_body = solid_body - slot_cut

for x in [-hole_spacing/2, hole_spacing/2]:
    hole_cut = Pos(x, 0, channel_height/2) * Cylinder(hole_diameter/2, channel_width + 10)
    solid_body = solid_body - hole_cut

front_face = solid_body.faces().sort_by(Axis.Y)[-1]
front_edges = front_face.edges()
solid_body = chamfer(front_edges, chamfer_size)

part = solid_body
part.name = "channel_with_slot_and_holes"
export_step(part, "output.step")
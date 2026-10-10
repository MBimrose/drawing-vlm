from build123d import *

channel_length = 80.0
channel_height = 40.0
channel_width = 30.0
wall_thickness = 2.0
slot_width = 10.0
slot_height = 20.0
slot_offset = 5.0
chamfer_size = 0.5
hole_diameter = 6.0

solid_body = Box(channel_length, channel_width, channel_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_z = channel_height/2 - slot_offset - slot_height/2
slot_box = Box(slot_width, channel_width + 10, slot_height)
solid_body = solid_body - Pos(0, 0, slot_z) * slot_box

hole_cyl = Cylinder(hole_diameter/2, channel_height + 10)
solid_body = solid_body - Pos(0, 0, 0) * hole_cyl

x_face = solid_body.faces().sort_by(Axis.X)[-1]
x_edges = x_face.edges()
solid_body = chamfer(x_edges, chamfer_size)

part = solid_body
part.name = "channel_with_slot_and_hole"
export_step(part, "output.step")
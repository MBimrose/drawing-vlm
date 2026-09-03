from build123d import *

channel_length = 80.0
channel_width = 20.0
channel_height = 30.0
wall_thickness = 1.0
hole_diameter = 5.5
hole_spacing = 15.0
hole_offset_from_bottom = 6.0
chamfer_size = 0.5

solid_body = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

hole1_z = hole_offset_from_bottom
hole2_z = hole_offset_from_bottom + hole_spacing
hole_tool = Rot(0, 90, 0) * Cylinder(hole_diameter/2, channel_length + 10)
solid_body = solid_body - Pos(-channel_length/2, 0, hole1_z) * hole_tool
solid_body = solid_body - Pos(-channel_length/2, 0, hole2_z) * hole_tool

part = solid_body
part.name = "channel_with_holes"
export_step(part, "output.step")
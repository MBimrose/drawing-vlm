from build123d import *

trough_length = 80.0
trough_width = 40.0
trough_height = 30.0
wall_thickness = 2.0
channel_width = 20.0
channel_depth = 20.0
fillet_radius = 0.5
mount_hole_diameter = 6.0
mount_hole_offset = 20.0

solid_body = Pos(0, 0, trough_height / 2) * Box(trough_length, trough_width, trough_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

channel = Pos(0, 0, channel_depth / 2) * Box(trough_length, channel_width, channel_depth)
solid_body = solid_body - channel

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

hole_x = -trough_length / 2 + mount_hole_offset
hole_z = trough_height / 2
hole = Pos(hole_x, trough_width / 2, hole_z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter / 2, trough_width + 10)
solid_body = solid_body - hole

part = solid_body
part.name = "trough"
export_step(part, "output.step")
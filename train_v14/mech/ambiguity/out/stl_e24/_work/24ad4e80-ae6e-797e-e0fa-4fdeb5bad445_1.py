from build123d import *

channel_length = 100.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 3.0
fillet_radius = 2.0
pocket_length = 80.0
pocket_width = 10.0
groove_width = 12.0
groove_depth = 4.0
groove_length = 70.0
hole_diameter = 5.0
hole_offset_from_edge = 5.0

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
base = fillet(base.edges(), fillet_radius)

top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

pocket = Pos(0, 0, channel_height/2) * Box(pocket_length, pocket_width, channel_height)
base = base - pocket

groove = Pos(0, 0, groove_depth/2) * Box(groove_length, groove_width, groove_depth)
base = base - groove

hole_center_x = channel_length / 2 - wall_thickness - hole_offset_from_edge
hole_center_y = -channel_width / 2 + wall_thickness + hole_offset_from_edge
hole = Pos(hole_center_x, hole_center_y, channel_height/2) * Cylinder(hole_diameter/2, channel_height)
base = base - hole

part = base
part.name = "channel_with_pocket_groove_hole"
export_step(part, "output.step")
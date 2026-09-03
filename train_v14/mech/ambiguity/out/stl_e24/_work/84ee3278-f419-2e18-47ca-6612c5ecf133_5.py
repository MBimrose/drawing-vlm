from build123d import *

chute_length = 80.0
chute_width = 40.0
chute_height = 30.0
wall_thickness = 2.0
channel_width = 20.0
channel_depth = 20.0
fillet_radius = 0.5
hole_diameter = 6.0
hole_offset_x = 20.0
hole_offset_z = 20.0

base = Pos(0, 0, chute_height/2) * Box(chute_length, chute_width, chute_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

channel = Pos(0, 0, channel_depth/2) * Box(chute_length, channel_width, channel_depth)
base = base - channel

hole_x = hole_offset_x - chute_length/2
hole_z = hole_offset_z - chute_height/2
hole = Pos(hole_x, 0, hole_z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, chute_width + 20)
base = base - hole

vertical_edges = base.edges().filter_by(Axis.Z)
base = fillet(vertical_edges, fillet_radius)

part = base
part.name = "chute"
export_step(part, "output.step")
from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.0
channel_cut_width = 20.0
channel_cut_depth = channel_height - 2 * wall_thickness
hole_diameter = 6.0
hole_offset_from_end = 20.0
chamfer_size = 0.5

base = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

cut_box = Pos(0, 0, wall_thickness) * Box(channel_length, channel_cut_width, channel_cut_depth)
base = base - cut_box

hole_x = -channel_length/2 + hole_offset_from_end
hole_y = channel_width/2
hole_z = channel_height/2
hole = Pos(hole_x, hole_y, hole_z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, channel_width)
base = base - hole

vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_size)

part = base
part.name = "channel"
export_step(part, "output.step")
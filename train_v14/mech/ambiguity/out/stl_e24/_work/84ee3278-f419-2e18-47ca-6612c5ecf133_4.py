from build123d import *

channel_length = 80.0
channel_width = 40.0
channel_height = 30.0
wall_thickness = 2.0
slot_width = 20.0
slot_depth = 15.0
hole_diameter = 6.0
hole_offset_from_end = 20.0
chamfer_size = 0.5

solid = Pos(0, 0, channel_height/2) * Box(channel_length, channel_width, channel_height)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = offset(solid, amount=-wall_thickness, openings=[top_face])

slot = Pos(0, 0, slot_depth/2) * Box(channel_length, slot_width, slot_depth)
solid = solid - slot

hole_x = -channel_length/2 + hole_offset_from_end
hole = Pos(hole_x, channel_width/2, channel_height/2) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, channel_width)
solid = solid - hole

vertical_edges = solid.edges().filter_by(Axis.Z)
solid = chamfer(vertical_edges, chamfer_size)

part = solid
part.name = "channel_with_slot_and_hole"
export_step(part, "output.step")
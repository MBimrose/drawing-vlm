from build123d import *

channel_width = 80.0
channel_depth = 30.0
channel_height = 40.0
wall_thickness = 2.0
pocket_width = 20.0
pocket_depth = 10.0
pocket_hole_diameter = 6.0
slot_width = 6.0
slot_length = 30.0
slot_spacing = 12.0
chamfer_size = 0.5

solid_body = Box(channel_width, channel_depth, channel_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket_cut = Pos(0, 0, channel_height/2 - pocket_depth/2) * Box(pocket_width, pocket_depth, pocket_depth)
solid_body = solid_body - pocket_cut

hole_cut = Pos(0, 0, channel_height/2 - pocket_depth/2) * Cylinder(pocket_hole_diameter/2, pocket_depth)
solid_body = solid_body - hole_cut

for z_offset in [-slot_spacing/2, slot_spacing/2]:
    slot_cut = Pos(0, channel_depth/2 - wall_thickness/2, channel_height/2 + z_offset) * Box(slot_width, wall_thickness, slot_length)
    solid_body = solid_body - slot_cut
    slot_cut = Pos(0, -channel_depth/2 + wall_thickness/2, channel_height/2 + z_offset) * Box(slot_width, wall_thickness, slot_length)
    solid_body = solid_body - slot_cut

front_face = solid_body.faces().sort_by(Axis.X)[-1]
front_edges = front_face.edges()
solid_body = chamfer(front_edges, chamfer_size)

part = solid_body
part.name = "channel_with_pockets_and_slots"
export_step(part, "output.step")
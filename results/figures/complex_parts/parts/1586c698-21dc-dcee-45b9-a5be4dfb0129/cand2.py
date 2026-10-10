from build123d import *

channel_length = 90.0
channel_width = 30.0
channel_height = 20.0
wall_thickness = 2.0
slot_width = 12.0
slot_height = 8.0
slot_offset_from_bottom = 5.0
chamfer_distance = 1.0
hole_diameter = 4.0
hole_spacing = 40.0
rib_thickness = 1.5
rib_height = channel_height - 2 * wall_thickness

solid_body = Pos(0, 0, channel_height / 2) * Box(channel_length, channel_width, channel_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_center_z = slot_offset_from_bottom + slot_height / 2
slot_cut = Pos(0, channel_width / 2 - wall_thickness / 2, slot_center_z) * Box(slot_width, wall_thickness, slot_height)
solid_body = solid_body - slot_cut

x_face = solid_body.faces().sort_by(Axis.X)[-1]
chamfer_edges = x_face.edges().filter_by(Axis.Z)
solid_body = chamfer(chamfer_edges, chamfer_distance)

for x_pos in [-hole_spacing / 2, hole_spacing / 2]:
    solid_body = solid_body - Pos(x_pos, 0, channel_height / 2) * Cylinder(hole_diameter / 2, channel_height + 10)

internal_rib = Pos(0, 0, wall_thickness + rib_height / 2) * Box(rib_thickness, channel_length, rib_height)
solid_body = solid_body + internal_rib

external_rib = Pos(0, -channel_width / 2 + wall_thickness / 2, wall_thickness + rib_height / 2) * Box(rib_thickness, channel_length, rib_height)
solid_body = solid_body + external_rib

part = solid_body
part.name = "channel_with_ribs"
export_step(part, "output.step")
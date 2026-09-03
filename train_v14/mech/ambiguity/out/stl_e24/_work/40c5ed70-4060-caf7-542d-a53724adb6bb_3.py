from build123d import *

channel_length = 80.0
channel_width = 50.0
channel_height = 30.0
wall_thickness = 3.0
slot_width = 20.0
slot_depth = 12.0
chamfer_size = 2.0
mount_hole_dia = 4.0
mount_hole_spacing = 30.0

solid = Pos(0, 0, channel_height / 2) * Box(channel_length, channel_width, channel_height)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = offset(solid, amount=-wall_thickness, openings=[top_face])

slot_cut = Pos(0, 0, channel_height - slot_depth / 2) * Box(slot_width, slot_depth, slot_depth)
solid = solid - slot_cut

bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = chamfer(bottom_face.edges(), chamfer_size)

hole_r = mount_hole_dia / 2
hole_h = channel_length + 20
for y in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    solid = solid - Pos(channel_length / 2, y, channel_height / 2) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
    solid = solid - Pos(-channel_length / 2, y, channel_height / 2) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)

part = solid
part.name = "channel_with_slot_and_mount_holes"
export_step(part, "output.step")
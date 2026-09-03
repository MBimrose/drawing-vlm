from build123d import *

frame_length = 80.0
frame_width = 60.0
frame_height = 15.0
wall_thickness = 5.0
rib_length = 60.0
rib_width = 10.0
rib_height = 3.0
mount_hole_diameter = 4.0
mount_hole_offset = 12.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 8.0
chamfer_size = 0.5

solid = Box(frame_length, frame_width, frame_height)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = offset(solid, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, 0, -frame_height/2 - rib_height/2) * Box(rib_length, rib_width, rib_height)
solid = solid + rib

hole_r = mount_hole_diameter / 2
hole_h = frame_height + rib_height + 10
for x, y in [(mount_hole_offset, mount_hole_offset),
             (frame_length - mount_hole_offset, mount_hole_offset),
             (mount_hole_offset, frame_width - mount_hole_offset),
             (frame_length - mount_hole_offset, frame_width - mount_hole_offset)]:
    solid = solid - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

pocket = Pos(0, 0, frame_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid = solid - pocket

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

part = solid
part.name = "frame_with_rib_and_pocket"
export_step(part, "output.step")
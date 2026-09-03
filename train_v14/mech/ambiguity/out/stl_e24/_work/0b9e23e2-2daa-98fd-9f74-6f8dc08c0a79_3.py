from build123d import *

block_length = 100.0
block_width = 60.0
block_height = 30.0
channel_radius = 20.0
channel_depth = 20.0
counterbore_diameter = 12.0
counterbore_depth = 4.0
through_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_offset = 8.0
rib_thickness = 5.0
rib_height = 5.0
chamfer_size = 0.5

solid_body = Box(block_length, block_width, block_height)

with BuildPart() as ch:
    with BuildSketch(Plane.XY.offset(block_height/2)) as sk:
        with BuildLine() as bl:
            l1 = Line((-channel_radius, 0), (channel_radius, 0))
            a1 = ThreePointArc(l1 @ 1, (channel_radius, channel_depth/2), (0, channel_depth))
            a2 = ThreePointArc(a1 @ 1, (-channel_radius, channel_depth/2), (-channel_radius, 0))
        make_face()
    extrude(amount=-channel_depth)
solid_body = solid_body - ch.part

solid_body = solid_body - Pos(0, block_width/2 - mount_hole_offset, block_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - Pos(0, block_width/2 - mount_hole_offset, 0) * Cylinder(through_hole_diameter/2, block_height + 10)

for x, y in [(-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
             (block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
             (-block_length/2 + mount_hole_offset, block_width/2 - mount_hole_offset),
             (block_length/2 - mount_hole_offset, block_width/2 - mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height + 10)

rib = Pos(0, 0, -block_height/2 + rib_height/2) * Box(block_length, rib_thickness, rib_height)
solid_body = solid_body + rib

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "block_with_channel_and_holes"
export_step(part, "output.step")
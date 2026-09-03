from build123d import *

block_length = 100.0
block_width = 60.0
block_height = 30.0
channel_radius = 10.0
channel_width = 2 * channel_radius
counterbore_diameter = 12.0
counterbore_depth = 4.0
through_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_offset = 8.0
rib_height = 5.0
rib_thickness = 4.0
rib_width = block_width - 2 * mount_hole_offset
pocket_width = 10.0
pocket_height = 5.0
pocket_depth = 5.0
pocket_spacing = 20.0
pocket_count = 2

solid_body = Box(block_length, block_width, block_height)

with BuildPart() as ch:
    with BuildSketch(Plane.XY.offset(block_height/2)) as sk:
        with BuildLine() as bl:
            l1 = Line((-channel_width/2, 0), (channel_width/2, 0))
            a1 = ThreePointArc(l1@1, (0, channel_radius), (-channel_width/2, 0))
        make_face()
    extrude(amount=-block_height/2)
solid_body = solid_body - ch.part

solid_body = solid_body - Pos(0, block_width/2 - mount_hole_offset, block_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - Pos(0, block_width/2 - mount_hole_offset, 0) * Cylinder(through_hole_diameter/2, block_height)

mount_points = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset,  block_width/2 - mount_hole_offset),
    (-block_length/2 + mount_hole_offset,  block_width/2 - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height)

rib = Pos(0, 0, block_height/2 - rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

for i in range(pocket_count):
    z_pos = -block_height/2 + mount_hole_offset + i * pocket_spacing
    solid_body = solid_body - Pos(block_length/2 - pocket_depth/2, block_width/2 - mount_hole_offset, z_pos) * Box(pocket_depth, pocket_width, pocket_height)

part = solid_body
part.name = "block_with_channel_and_features"
export_step(part, "output.step")
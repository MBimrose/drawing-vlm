from build123d import *

block_length = 100.0
block_width = 60.0
block_height = 30.0
wall_thickness = 5.0
channel_width = 40.0
channel_depth = 20.0
channel_radius = 10.0
counterbore_diameter = 12.0
counterbore_depth = 8.0
through_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_offset = 8.0
chamfer_size = 1.0

base = Box(block_length, block_width, block_height)

with BuildPart() as ch:
    with BuildSketch(Plane.XY.offset(block_height/2)) as sk:
        with BuildLine() as bl:
            l1 = Line((-channel_width/2, 0), (-channel_width/2, channel_depth - channel_radius))
            a1 = ThreePointArc(l1@1, (0, channel_depth), (channel_width/2, channel_depth - channel_radius))
            l2 = Line(a1@1, (channel_width/2, 0))
            l3 = Line(l2@1, l1@0)
        make_face()
    extrude(amount=-channel_depth)
channel_solid = ch.part

result = base - channel_solid

cbore = Pos(0, channel_depth/2, block_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
result = result - cbore

thru = Pos(0, channel_depth/2, 0) * Cylinder(through_hole_diameter/2, block_height + 10)
result = result - thru

for x, y in [(-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
             (block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
             (-block_length/2 + mount_hole_offset, block_width/2 - mount_hole_offset),
             (block_length/2 - mount_hole_offset, block_width/2 - mount_hole_offset)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height + 10)

chamfer_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2] + result.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
result = chamfer(chamfer_edges, chamfer_size)

part = result
part.name = "channel_block"
export_step(part, "output.step")
from build123d import *

block_length = 100.0
block_width = 60.0
block_height = 30.0
pocket_width = 20.0
pocket_depth = 20.0
pocket_radius = pocket_width / 2.0
counterbore_diameter = 12.0
counterbore_depth = 4.0
through_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_offset = 8.0
chamfer_size = 0.5
side_pocket_width = 10.0
side_pocket_depth = 5.0
side_pocket_offset = 5.0

result = Box(block_length, block_width, block_height)

with BuildPart() as pocket_bp:
    with BuildSketch(Plane.XY.offset(block_height/2)) as ps:
        with BuildLine() as pl:
            l1 = Line((-pocket_width, 0), (pocket_width, 0))
            a1 = ThreePointArc(l1 @ 1, (pocket_width, pocket_radius), (0, pocket_radius + pocket_width))
            l2 = Line(a1 @ 1, (-pocket_width, pocket_radius))
            a2 = ThreePointArc(l2 @ 1, (-pocket_width, pocket_radius/2), (-pocket_width, 0))
        make_face()
    extrude(amount=-pocket_depth)
result = result - pocket_bp.part

cbore = Pos(0, pocket_radius + pocket_width/2, block_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
result = result - cbore

thru = Pos(0, pocket_radius + pocket_width/2, 0) * Cylinder(through_hole_diameter/2, block_height + 10)
result = result - thru

for x, y in [(-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
             (block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
             (-block_length/2 + mount_hole_offset, block_width/2 - mount_hole_offset),
             (block_length/2 - mount_hole_offset, block_width/2 - mount_hole_offset)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height + 10)

sp1 = Pos(block_length/2 - side_pocket_depth/2, side_pocket_offset, -block_height/4) * Box(side_pocket_depth, side_pocket_width, side_pocket_depth)
result = result - sp1

sp2 = Pos(-block_length/2 + side_pocket_depth/2, -side_pocket_offset, -block_height/4) * Box(side_pocket_depth, side_pocket_width, side_pocket_depth)
result = result - sp2

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "block_with_pockets"
export_step(part, "output.step")
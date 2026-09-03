from build123d import *

block_length = 100.0
block_width = 60.0
block_height = 30.0
pocket_width = 40.0
pocket_height = 20.0
pocket_depth = 20.0
counterbore_diameter = 12.0
counterbore_depth = 4.0
through_hole_diameter = 6.0
mount_hole_diameter = 4.0
mount_hole_offset = 8.0
chamfer_size = 0.5
slot_width = 5.0
slot_height = 10.0
slot_depth = 5.0
slot_offset = 20.0

result = Box(block_length, block_width, block_height)

with BuildPart() as pocket_bp:
    with BuildSketch(Plane.XY.offset(block_height/2)) as ps:
        with BuildLine() as pl:
            l1 = Line((-pocket_width/2, 0), (pocket_width/2, 0))
            a1 = ThreePointArc(l1@1, (pocket_width/2, pocket_height/2), (0, pocket_height))
            a2 = ThreePointArc(a1@1, (-pocket_width/2, pocket_height/2), (-pocket_width/2, 0))
        make_face()
    extrude(amount=-pocket_depth)
result = result - pocket_bp.part

result = result - Pos(0, pocket_height/2, block_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
result = result - Pos(0, pocket_height/2, 0) * Cylinder(through_hole_diameter/2, block_height)

corner_x = block_length/2 - mount_hole_offset
corner_y = block_width/2 - mount_hole_offset
for x, y in [(corner_x, corner_y), (-corner_x, corner_y), (-corner_x, -corner_y), (corner_x, -corner_y)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height)

result = result - Pos(block_length/2 - slot_depth/2, slot_offset, -block_height/4) * Box(slot_depth, slot_width, slot_height)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "block_with_pocket_and_holes"
export_step(part, "output.step")
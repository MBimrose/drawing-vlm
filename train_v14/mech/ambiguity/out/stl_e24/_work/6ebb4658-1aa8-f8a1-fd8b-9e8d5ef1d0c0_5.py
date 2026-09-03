from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
boss_diameter = 20.0
boss_height = 10.0
through_hole_diameter = 12.0
counterbore_diameter = 20.0
counterbore_depth = 10.0
chamfer_size = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 5.0

solid_body = Box(block_length, block_width, block_height)
solid_body = solid_body + Pos(0, 0, block_height/2 - boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body - Cylinder(through_hole_diameter/2, block_height + boss_height)
solid_body = solid_body - Pos(0, 0, block_height/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

mount_hole = Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width + 10)
for x in [-block_length/2 + mount_hole_offset, block_length/2 - mount_hole_offset]:
    for z in [block_height/2 - mount_hole_offset, -block_height/2 + mount_hole_offset]:
        solid_body = solid_body - Pos(x, 0, z) * mount_hole

top_edges = solid_body.faces().sort_by(Axis.Z)[-1].edges()
bottom_edges = solid_body.faces().sort_by(Axis.Z)[0].edges()
solid_body = chamfer(top_edges + bottom_edges, chamfer_size)

part = solid_body
part.name = "block_with_boss_and_holes"
export_step(part, "output.step")
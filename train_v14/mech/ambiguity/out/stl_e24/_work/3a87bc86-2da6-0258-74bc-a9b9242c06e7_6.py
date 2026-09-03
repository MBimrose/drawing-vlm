from build123d import *

block_length = 80.0
block_width = 60.0
block_height = 20.0
central_hole_dia = 20.0
mount_hole_dia = 5.0
mount_hole_spacing = 30.0
rib_thickness = 4.0
rib_height = 5.0
chamfer_dist = 2.0
pocket_depth = 10.0
pocket_width = 40.0
pocket_length = 30.0

solid_body = Box(block_length, block_width, block_height)
solid_body = solid_body - Cylinder(central_hole_dia / 2, block_height)

for dx in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    for dy in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
        solid_body = solid_body - Pos(dx, dy, 0) * Cylinder(mount_hole_dia / 2, block_height)

solid_body = solid_body - Pos(0, 0, block_height - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)

rib = Pos(0, 0, block_height / 2 - rib_height / 2) * Box(block_length - 2 * rib_thickness, block_width - 2 * rib_thickness, rib_height)
solid_body = solid_body + rib

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_dist)

part = solid_body
part.name = "block_with_holes_pocket_rib"
export_step(part, "output.step")
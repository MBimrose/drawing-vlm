from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
corner_radius = 5.0
chamfer_size = 1.0
central_hole_diameter = 12.0
mount_hole_diameter = 4.2
mount_hole_spacing = 30.0
pocket_depth = 5.0
pocket_margin = 5.0

solid = Box(block_length, block_width, block_height)
solid = fillet(solid.edges().filter_by(Axis.Y), corner_radius)
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)
solid = solid - Pos(0, 0, block_height/2) * Cylinder(central_hole_diameter/2, block_height)
for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2),
             (mount_hole_spacing/2, -mount_hole_spacing/2),
             (-mount_hole_spacing/2, mount_hole_spacing/2),
             (mount_hole_spacing/2, mount_hole_spacing/2)]:
    solid = solid - Pos(x, y, block_height/2) * Cylinder(mount_hole_diameter/2, block_height)
pocket_w = block_width - 2 * pocket_margin
pocket_l = block_length - 2 * pocket_margin
solid = solid - Pos(0, 0, block_height - pocket_depth/2) * Box(pocket_w, pocket_l, pocket_depth)

part = solid
part.name = "block_with_holes_and_pocket"
export_step(part, "output.step")
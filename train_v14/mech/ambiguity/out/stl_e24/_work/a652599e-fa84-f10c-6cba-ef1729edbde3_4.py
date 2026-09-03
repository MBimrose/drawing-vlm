from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
corner_radius = 5.0
central_hole_diameter = 12.0
central_hole_depth = 12.0
mount_hole_diameter = 4.2
mount_hole_spacing = 30.0
chamfer_size = 1.0

solid_body = Box(block_length, block_width, block_height)
solid_body = fillet(solid_body.edges().filter_by(Axis.Y), corner_radius)
solid_body = solid_body - Pos(0, 0, block_height/2 - central_hole_depth/2) * Cylinder(central_hole_diameter/2, central_hole_depth)
for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2),
             (mount_hole_spacing/2, -mount_hole_spacing/2),
             (-mount_hole_spacing/2, mount_hole_spacing/2),
             (mount_hole_spacing/2, mount_hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, block_height/2) * Cylinder(mount_hole_diameter/2, block_height)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "block_with_holes_and_chamfers"
export_step(part, "output.step")
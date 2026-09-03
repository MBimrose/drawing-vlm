from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
fillet_radius = 5.0
chamfer_distance = 1.0
blind_hole_diameter = 12.0
blind_hole_depth = 12.0
mount_hole_diameter = 4.2
mount_hole_spacing = 30.0
rib_width = 6.0
rib_height = 6.0

base = Box(block_length, block_width, block_height)
rib = Pos(0, 0, -block_height/2 + rib_height/2) * Box(block_length, rib_width, rib_height)
solid_body = base + rib

solid_body = fillet(solid_body.edges().filter_by(Axis.Y), fillet_radius)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

solid_body = solid_body - Pos(0, 0, block_height/2 - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2),
             (mount_hole_spacing/2, -mount_hole_spacing/2),
             (-mount_hole_spacing/2, mount_hole_spacing/2),
             (mount_hole_spacing/2, mount_hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, block_height/2) * Cylinder(mount_hole_diameter/2, block_height)

part = solid_body
part.name = "block_with_rib_and_holes"
export_step(part, "output.step")
from build123d import *

block_length = 70.0
block_width = 40.0
block_height = 20.0
rib_length = 50.0
rib_width = 12.0
rib_height = 8.0
central_hole_diameter = 10.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
chamfer_distance = 2.0
fillet_radius = 2.0

solid_body = Box(block_length, block_width, block_height)
rib = Pos(0, 0, block_height/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

solid_body = solid_body - Cylinder(central_hole_diameter/2, 100)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, block_height/2 + rib_height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, 100)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "block_with_rib_and_holes"
export_step(part, "output.step")
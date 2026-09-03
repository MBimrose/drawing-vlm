from build123d import *

block_length = 70
block_width = 40
block_height = 20
rib_length = 50
rib_width = 12
rib_height = 8
central_hole_dia = 10
fillet_radius = 2
chamfer_distance = 1
mount_hole_dia = 4
mount_hole_spacing = 30

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)
rib = Pos(0, 0, block_height + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = base + rib

solid_body = solid_body - Pos(0, 0, (block_height + rib_height)/2) * Cylinder(central_hole_dia/2, block_height + rib_height + 10)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, block_height + rib_height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_dia/2, block_width + 10)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

part = solid_body
part.name = "ribbed_block_with_holes"
export_step(part, "output.step")
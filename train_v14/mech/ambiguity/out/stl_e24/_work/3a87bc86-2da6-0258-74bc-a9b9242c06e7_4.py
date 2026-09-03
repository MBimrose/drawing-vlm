from build123d import *

block_length = 80.0
block_width = 60.0
block_height = 20.0
central_hole_diameter = 20.0
rib_height = 5.0
rib_offset = 4.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
chamfer_distance = 2.0

solid_body = Box(block_length, block_width, block_height)

solid_body = solid_body - Cylinder(central_hole_diameter / 2, block_height * 2)

for x, y in [(-mount_hole_spacing/2, -mount_hole_spacing/2),
             (mount_hole_spacing/2, -mount_hole_spacing/2),
             (-mount_hole_spacing/2, mount_hole_spacing/2),
             (mount_hole_spacing/2, mount_hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, block_height * 2)

rib = Pos(0, 0, block_height/2 - rib_height/2) * Box(block_length - 2*rib_offset, block_width - 2*rib_offset, rib_height)
solid_body = solid_body + rib

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "block_with_rib_and_holes"
export_step(part, "output.step")
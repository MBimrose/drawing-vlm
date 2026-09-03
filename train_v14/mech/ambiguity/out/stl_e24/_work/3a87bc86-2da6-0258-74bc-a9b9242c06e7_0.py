from build123d import *

block_length = 80.0
block_width = 60.0
block_height = 20.0
central_hole_diameter = 20.0
rib_height = 5.0
rib_offset = 4.0
mount_hole_diameter = 5.0
mount_hole_offset = 12.0
chamfer_distance = 2.0

base = Box(block_length, block_width, block_height)
base = base - Cylinder(central_hole_diameter/2, block_height)

rib = Pos(0, 0, block_height/2 - rib_height/2) * Box(block_length - 2*rib_offset, block_width - 2*rib_offset, rib_height)
result = base + rib

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (mount_hole_offset, -mount_hole_offset), (-mount_hole_offset, -mount_hole_offset)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "block_with_rib_and_holes"
export_step(part, "output.step")
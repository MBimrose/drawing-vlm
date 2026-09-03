from build123d import *

block_length = 80.0
block_width = 60.0
block_height = 20.0
central_hole_dia = 20.0
rib_height = 5.0
rib_offset = 4.0
mount_hole_dia = 5.0
mount_hole_spacing = 30.0
chamfer_size = 2.0

base = Box(block_length, block_width, block_height)
base = base - Cylinder(central_hole_dia / 2, block_height)

rib = Pos(0, 0, block_height / 2 - rib_height / 2) * Box(block_length - 2 * rib_offset, block_width - 2 * rib_offset, rib_height)
base = base + rib

for i in range(2):
    for j in range(2):
        x = (i - 0.5) * mount_hole_spacing
        y = (j - 0.5) * mount_hole_spacing
        base = base - Pos(x, y, 0) * Cylinder(mount_hole_dia / 2, block_height)

base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

part = base
part.name = "block_with_rib_and_holes"
export_step(part, "output.step")
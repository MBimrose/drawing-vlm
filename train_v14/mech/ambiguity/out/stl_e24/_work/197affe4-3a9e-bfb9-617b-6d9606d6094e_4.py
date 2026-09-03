from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 15.0
rib_thickness = 3.0
rib_height = 12.0
mount_hole_dia = 5.0
mount_hole_spacing = 35.0

base = Box(block_length, block_width, block_height)
pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

rib1 = Pos(0, 0, block_height/2 - pocket_depth + rib_height/2) * Box(pocket_length - 2*rib_thickness, rib_thickness, rib_height)
rib2 = Pos(0, 0, block_height/2 - pocket_depth + rib_height/2) * Box(rib_thickness, pocket_width - 2*rib_thickness, rib_height)

result = base + rib1 + rib2

hole = Rot(90, 0, 0) * Cylinder(mount_hole_dia/2, block_width + 10)
for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(x, 0, 0) * hole

part = result
part.name = "block_with_pocket_ribs_and_holes"
export_step(part, "output.step")
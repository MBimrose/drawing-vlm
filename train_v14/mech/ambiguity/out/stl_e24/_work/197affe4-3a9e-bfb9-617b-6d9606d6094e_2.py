from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
pocket_length = 40.0
pocket_width = 25.0
pocket_depth = 15.0
chamfer_size = 1.0
blind_hole_diameter = 8.0
blind_hole_depth = 12.0
mount_hole_diameter = 5.0
mount_hole_spacing = 35.0
rib_thickness = 5.0
rib_height = 15.0

result = Box(block_length, block_width, block_height)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

blind_hole = Pos(0, 0, block_height/2 - pocket_depth - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
result = result - blind_hole

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    mount_hole = Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width)
    result = result - mount_hole

rib = Pos(0, 0, -block_height/2 + rib_height/2) * Box(block_length, rib_thickness, rib_height)
result = result + rib

part = result
part.name = "block_with_pocket_and_rib"
export_step(part, "output.step")
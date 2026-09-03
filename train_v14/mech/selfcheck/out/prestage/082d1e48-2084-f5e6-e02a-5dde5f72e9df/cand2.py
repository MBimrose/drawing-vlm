from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 5.0
pocket_length = 50.0
pocket_width = 30.0
pocket_depth = block_height - wall_thickness
fillet_radius = 2.0
mount_hole_diameter = 8.0
rib_width = 6.0
rib_height = 4.0
rib_spacing = 12.0
rib_depth = wall_thickness

result = Box(block_length, block_width, block_height)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

hole = Pos(block_length/2, 0, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, block_length)
result = result - hole

num_ribs = int((pocket_length - 2 * rib_spacing) // rib_spacing) + 1
for i in range(num_ribs):
    x = -pocket_length/2 + rib_spacing + i * rib_spacing
    rib = Pos(x, 0, block_height/2 - rib_depth/2) * Box(rib_width, rib_height, rib_depth)
    result = result - rib

part = result
part.name = "block_with_pocket_and_ribs"
export_step(part, "output.step")
from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
rib_width = 2.0
rib_height = 5.0
rib_spacing = 15.0
hole_diameter = 6.0
hole_depth = 4.0
hole_spacing = 20.0
chamfer_distance = 2.0

solid_body = Box(block_length, block_width, block_height)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

num_ribs_x = int((block_length - rib_spacing) // rib_spacing) + 1
num_ribs_y = int((block_width - rib_spacing) // rib_spacing) + 1
for i in range(num_ribs_x):
    for j in range(num_ribs_y):
        x = -block_length/2 + rib_spacing/2 + i * rib_spacing
        y = -block_width/2 + rib_spacing/2 + j * rib_spacing
        solid_body = solid_body + Pos(x, y, block_height + rib_height/2) * Box(rib_width, rib_width, rib_height)

for i in range(3):
    x = -hole_spacing + i * hole_spacing
    solid_body = solid_body - Pos(x, block_width/2 - hole_depth/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - Pos(x, -block_width/2 + hole_depth/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, hole_depth)

part = solid_body
part.name = "ribbed_block_with_holes"
export_step(part, "output.step")
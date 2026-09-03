from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
rib_width = 2.0
rib_depth = 2.0
rib_height = 5.0
rib_spacing_x = 15.0
rib_spacing_y = 15.0
hole_diameter = 6.0
hole_depth = 4.0
hole_spacing = 20.0
chamfer_distance = 2.0

solid_body = Box(block_length, block_width, block_height)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

rib_count_x = int((block_length - rib_spacing_x) // rib_spacing_x) + 1
rib_count_y = int((block_width - rib_spacing_y) // rib_spacing_y) + 1
for i in range(rib_count_x):
    for j in range(rib_count_y):
        x = (i - (rib_count_x - 1) / 2) * rib_spacing_x
        y = (j - (rib_count_y - 1) / 2) * rib_spacing_y
        solid_body = solid_body + Pos(x, y, block_height + rib_height/2) * Box(rib_width, rib_depth, rib_height)

for i in range(3):
    x = (i - 1) * hole_spacing
    solid_body = solid_body - Pos(x, block_width/2 - hole_depth/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - Pos(x, -block_width/2 + hole_depth/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, hole_depth)

part = solid_body
part.name = "ribbed_block_with_holes"
export_step(part, "output.step")
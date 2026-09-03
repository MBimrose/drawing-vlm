from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
rib_thickness = 2.0
rib_height = 5.0
rib_spacing_x = 15.0
rib_spacing_y = 15.0
rib_count_x = 5
rib_count_y = 3
hole_diameter = 6.0
hole_depth = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_count_x = 3
hole_count_y = 1
chamfer_distance = 2.0

solid_body = Box(block_length, block_width, block_height)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

for i in range(rib_count_x):
    for j in range(rib_count_y):
        x = (i - (rib_count_x - 1) / 2) * rib_spacing_x
        y = (j - (rib_count_y - 1) / 2) * rib_spacing_y
        solid_body = solid_body + Pos(x, y, block_height + rib_height / 2) * Box(rib_thickness, rib_thickness, rib_height)

for i in range(hole_count_x):
    x = (i - (hole_count_x - 1) / 2) * hole_spacing_x
    solid_body = solid_body - Pos(x, block_width / 2 - hole_depth / 2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, hole_depth)
    solid_body = solid_body - Pos(x, -block_width / 2 + hole_depth / 2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, hole_depth)

part = solid_body
part.name = "ribbed_block_with_holes"
export_step(part, "output.step")
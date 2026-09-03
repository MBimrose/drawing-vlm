from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
rib_thickness = 2.0
rib_height = 5.0
rib_spacing = 15.0
rib_margin = 10.0
hole_diameter = 6.0
hole_depth = 8.0
hole_spacing = 20.0
hole_margin = 10.0
chamfer_distance = 2.0

solid_body = Box(block_length, block_width, block_height)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

num_ribs_x = int((block_length - 2 * rib_margin) // rib_spacing) + 1
num_ribs_y = int((block_width - 2 * rib_margin) // rib_spacing) + 1
for i in range(num_ribs_x):
    for j in range(num_ribs_y):
        x = -block_length / 2 + rib_margin + i * rib_spacing
        y = -block_width / 2 + rib_margin + j * rib_spacing
        solid_body = solid_body + Pos(x, y, block_height + rib_height / 2) * Box(rib_thickness, rib_thickness, rib_height)

num_holes_x = int((block_length - 2 * hole_margin) // hole_spacing) + 1
for i in range(num_holes_x):
    x = -block_length / 2 + hole_margin + i * hole_spacing
    solid_body = solid_body - Pos(x, block_width / 2 - hole_depth / 2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, hole_depth)
    solid_body = solid_body - Pos(x, -block_width / 2 + hole_depth / 2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, hole_depth)

part = solid_body
part.name = "ribbed_block_with_holes"
export_step(part, "output.step")
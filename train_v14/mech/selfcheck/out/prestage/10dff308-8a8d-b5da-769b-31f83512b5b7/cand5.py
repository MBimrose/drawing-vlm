from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
rib_height = 5.0
rib_thickness = 2.0
rib_spacing = 15.0
hole_diameter = 6.0
hole_depth = 4.0
hole_spacing = 20.0
chamfer_distance = 2.0

solid_body = Box(block_length, block_width, block_height)
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

nx = int((block_length - rib_spacing) // rib_spacing) + 1
ny = int((block_width - rib_spacing) // rib_spacing) + 1

for i in range(nx):
    for j in range(ny):
        x = (i - (nx - 1) / 2) * rib_spacing
        y = (j - (ny - 1) / 2) * rib_spacing
        rib = Pos(x, y, block_height + rib_height / 2) * Box(rib_thickness, rib_thickness, rib_height)
        solid_body = solid_body + rib

for i in range(3):
    x = (i - 1) * hole_spacing
    hole = Pos(x, block_width / 2 - hole_depth / 2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, hole_depth)
    solid_body = solid_body - hole

for i in range(3):
    x = (i - 1) * hole_spacing
    hole = Pos(x, -block_width / 2 + hole_depth / 2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, hole_depth)
    solid_body = solid_body - hole

part = solid_body
part.name = "ribbed_block_with_holes"
export_step(part, "output.step")
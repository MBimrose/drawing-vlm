from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
wall_thickness = 4.0
rib_width = 6.0
rib_spacing = 12.0
rib_height = 12.0
hole_diameter = 4.0
hole_depth = 8.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
hole_rows = 2
hole_cols = 2
chamfer_size = 1.2
fillet_radius = 0.8

solid_body = Box(block_length, block_width, block_height)

rib_count = int((block_length - 2 * wall_thickness) // (rib_width + rib_spacing))
for i in range(rib_count):
    x_pos = -block_length / 2 + wall_thickness + rib_width / 2 + i * (rib_width + rib_spacing)
    rib = Pos(x_pos, 0, rib_height / 2) * Box(rib_width, block_width, rib_height)
    solid_body = solid_body + rib

pocket = Pos(0, 0, block_height - wall_thickness / 2) * Box(block_length - 2 * wall_thickness, block_width - 2 * wall_thickness, wall_thickness)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, -block_height / 2 + hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)
        solid_body = solid_body - hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "ribbed_block_with_pocket"
export_step(part, "output.step")
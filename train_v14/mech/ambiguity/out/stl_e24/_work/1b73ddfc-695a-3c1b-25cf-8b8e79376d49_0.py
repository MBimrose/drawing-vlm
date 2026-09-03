from build123d import *

block_length = 60.0
block_width = 40.0
block_thickness = 8.0
rib_width = 6.0
rib_height = 4.0
rib_spacing = 12.0
rib_count = 3
hole_diameter = 4.0
cbore_diameter = 5.0
cbore_depth = 4.0

solid_body = Box(block_length, block_width, block_thickness)

for i in range(rib_count):
    x_offset = -block_length/2 + rib_spacing + i * rib_spacing
    rib = Pos(x_offset, 0, rib_height/2) * Box(rib_width, block_width, rib_height)
    solid_body = solid_body + rib

solid_body = solid_body - Cylinder(hole_diameter/2, block_thickness)
solid_body = solid_body - Pos(0, 0, -block_thickness/2 + cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)

part = solid_body
part.name = "ribbed_block_with_cbore"
export_step(part, "output.step")
from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
rib_thickness = 2.0
rib_height = 5.0
rib_spacing = 15.0
hole_diameter = 6.0
hole_depth = 4.0
hole_spacing = 20.0
chamfer_distance = 2.0

result = Box(block_length, block_width, block_height)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

nx = int((block_length - 2 * rib_spacing) // rib_spacing) + 1
ny = int((block_width - 2 * rib_spacing) // rib_spacing) + 1
for i in range(nx):
    for j in range(ny):
        x = -block_length/2 + rib_spacing + i * rib_spacing
        y = -block_width/2 + rib_spacing + j * rib_spacing
        result = result + Pos(x, y, block_height + rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)

for i in range(3):
    x = -hole_spacing + i * hole_spacing
    result = result - Pos(x, block_width/2 - hole_depth/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, hole_depth)
    result = result - Pos(x, -block_width/2 + hole_depth/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, hole_depth)

part = result
part.name = "ribbed_block_with_holes"
export_step(part, "output.step")
from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
bearing_diameter = 20.0
bearing_depth = 10.0
shaft_diameter = 12.0
shaft_depth = 20.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
rib_thickness = 4.0
rib_height = 5.0
rib_spacing = 15.0
chamfer_distance = 1.0

result = Box(block_length, block_width, block_height)

result = result - Pos(0, 0, block_height/2 - bearing_depth/2) * Cylinder(bearing_diameter/2, bearing_depth)
result = result - Pos(0, 0, block_height/2 - shaft_depth/2) * Cylinder(shaft_diameter/2, shaft_depth)

for x in [-block_length/2 + mount_hole_offset/2, block_length/2 - mount_hole_offset/2]:
    for z in [mount_hole_offset/2, block_height - mount_hole_offset/2]:
        result = result - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width + 10)

rib_count = int((block_length - rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -block_length/2 + rib_spacing/2 + i * rib_spacing
    result = result + Pos(x_pos, 0, -block_height/2 + rib_height/2) * Box(rib_thickness, block_width - 2*mount_hole_offset, rib_height)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

part = result
part.name = "bearing_block_with_ribs"
export_step(part, "output.step")
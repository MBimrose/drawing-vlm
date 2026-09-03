from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
bearing_diameter = 32.0
bearing_depth = 12.0
bearing_offset_x = 20.0
bearing_offset_y = 15.0
through_hole_diameter = 6.0
through_hole_offset_x = 10.0
through_hole_offset_y = 10.0
fillet_radius = 2.0
mount_hole_diameter = 4.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 20.0
rib_height = 4.0
rib_width = 30.0
rib_length = 40.0
slot_width = 6.0
slot_length = 20.0
slot_offset_x = 15.0

result = Box(block_length, block_width, block_height)

bearing_x = bearing_offset_x - block_length / 2
bearing_y = bearing_offset_y - block_width / 2
result = result - Pos(bearing_x, bearing_y, block_height - bearing_depth / 2) * Cylinder(bearing_diameter / 2, bearing_depth)

through_x = through_hole_offset_x - block_length / 2
through_y = through_hole_offset_y - block_width / 2
result = result - Pos(through_x, through_y, 0) * Cylinder(through_hole_diameter / 2, block_height)

for i in range(2):
    for j in range(2):
        mx = (i - 0.5) * mount_hole_spacing_x
        my = (j - 0.5) * mount_hole_spacing_y
        result = result - Pos(mx, my, 0) * Cylinder(mount_hole_diameter / 2, block_height)

result = result + Pos(0, 0, block_height / 2 - rib_height / 2) * Box(rib_length, rib_width, rib_height)

slot_x = slot_offset_x - block_length / 2
result = result - Pos(block_length / 2 - block_height / 4, 0, slot_x) * Box(block_height / 2, slot_width, slot_length)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "bearing_block"
export_step(part, "output.step")
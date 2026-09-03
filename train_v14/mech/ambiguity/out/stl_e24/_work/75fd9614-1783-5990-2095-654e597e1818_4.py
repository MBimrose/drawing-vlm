from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
bearing_diameter = 32.0
bearing_depth = 20.0
bearing_offset_x = 20.0
bearing_offset_y = 15.0
through_hole_diameter = 6.0
fillet_radius = 2.0
rib_height = 4.0
rib_width = 20.0
rib_length = 40.0
rib_offset_x = 10.0
mount_hole_diameter = 4.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 20.0
slot_width = 6.0
slot_length = 20.0
slot_depth = 5.0

result = Box(block_length, block_width, block_height)

rib = Pos(-block_length/2 + rib_offset_x + rib_length/2, 0, block_height/2 - rib_height/2) * Box(rib_length, rib_width, rib_height)
result = result + rib

bearing_center_x = -block_length/2 + bearing_offset_x
bearing_center_y = -block_width/2 + bearing_offset_y
bearing_cut = Pos(bearing_center_x, bearing_center_y, block_height/2 - bearing_depth/2) * Cylinder(bearing_diameter/2, bearing_depth)
result = result - bearing_cut

through_hole = Pos(bearing_center_x, bearing_center_y, 0) * Cylinder(through_hole_diameter/2, block_height + 10)
result = result - through_hole

for dx in [-mount_hole_spacing_x/2, mount_hole_spacing_x/2]:
    for dy in [-mount_hole_spacing_y/2, mount_hole_spacing_y/2]:
        mount_hole = Pos(dx, dy, 0) * Cylinder(mount_hole_diameter/2, block_height + 10)
        result = result - mount_hole

slot_cut = Pos(block_length/2 - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, slot_length)
result = result - slot_cut

vertical_edges = result.edges().filter_by(Axis.Z)
result = fillet(vertical_edges, fillet_radius)

part = result
part.name = "bearing_block"
export_step(part, "output.step")
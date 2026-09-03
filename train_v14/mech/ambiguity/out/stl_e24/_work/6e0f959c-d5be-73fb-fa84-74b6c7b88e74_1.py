from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 15.0
wall_thickness = 2.0
channel_depth = 8.0
channel_width = block_width - 2 * wall_thickness
channel_length = block_length - 2 * wall_thickness
blind_hole_diameter = 6.0
blind_hole_depth = 10.0
fillet_radius = 0.5
chamfer_distance = 1.0
rib_thickness = 1.5
rib_height = block_height - 2 * wall_thickness
rib_length = block_width / 2
mount_hole_diameter = 2.5
mount_hole_offset = 12.0

result = Box(block_length, block_width, block_height)

channel_cut = Pos(0, -block_width/2 + wall_thickness/2, 0) * Box(channel_length, wall_thickness, channel_depth)
result = result - channel_cut

blind_hole = Pos(block_length/2 - blind_hole_depth/2, -block_width/2 + wall_thickness + 10, 0) * Rot(0, 90, 0) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
result = result - blind_hole

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (mount_hole_offset, -mount_hole_offset), (-mount_hole_offset, -mount_hole_offset)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height)

rib = Pos(block_length/2 - wall_thickness - rib_thickness/2, -block_width/2 + wall_thickness + rib_length/2, 0) * Box(rib_thickness, rib_length, rib_height)
result = result + rib

vertical_edges = result.edges().filter_by(Axis.Z)
sorted_by_y = vertical_edges.sort_by(Axis.Y)
chamfer_edges = sorted_by_y[:2] + sorted_by_y[-2:]
result = chamfer(chamfer_edges, chamfer_distance)

bottom_face = result.faces().sort_by(Axis.Y)[0]
result = fillet(bottom_face.edges(), fillet_radius)

part = result
part.name = "channel_block_with_rib"
export_step(part, "output.step")
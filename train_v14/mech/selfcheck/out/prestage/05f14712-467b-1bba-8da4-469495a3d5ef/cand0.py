from build123d import *

block_length = 70.0
block_width = 50.0
block_height = 30.0
wall_thickness = 5.0
hole_diameter = 12.0
hole_spacing = 30.0
fillet_radius = 1.0
chamfer_distance = 1.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
rib_height = 5.0
rib_width = 5.0
pocket_length = 20.0
pocket_width = 30.0
pocket_depth = 10.0
cross_hole_diameter = 6.0
cross_hole_offset = 15.0

solid_body = Box(block_length, block_width, block_height)

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, block_height)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

mount_points = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    (-block_length/2 + mount_hole_offset,  block_width/2 - mount_hole_offset),
    ( block_length/2 - mount_hole_offset,  block_width/2 - mount_hole_offset)
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height)

solid_body = solid_body + Pos(0, 0, rib_height/2) * Box(block_length, rib_width, rib_height)

solid_body = solid_body - Pos(-block_length/4, 0, -block_height/2 + pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

solid_body = solid_body - Pos(0, 0, cross_hole_offset) * Rot(0, 90, 0) * Cylinder(cross_hole_diameter/2, block_length)

part = solid_body
part.name = "block_with_holes_and_features"
export_step(part, "output.step")
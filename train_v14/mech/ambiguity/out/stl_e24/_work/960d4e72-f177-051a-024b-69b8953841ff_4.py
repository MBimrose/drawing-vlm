from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
bearing_radius = 12.0
bearing_depth = 8.0
boss_radius = 8.0
boss_height = 10.0
chamfer_size = 1.0
hole_diameter = 5.0
hole_spacing = 30.0

solid_body = Box(block_length, block_width, block_height)
solid_body = solid_body + Pos(block_length/2 - boss_height/2, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body - Pos(block_length/2, 0, 0) * Rot(0, 90, 0) * Cylinder(bearing_radius, bearing_depth)

for x, y in [(-hole_spacing/2, -hole_spacing/2), (hole_spacing/2, -hole_spacing/2),
             (-hole_spacing/2, hole_spacing/2), (hole_spacing/2, hole_spacing/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "block_with_boss_and_holes"
export_step(part, "output.step")
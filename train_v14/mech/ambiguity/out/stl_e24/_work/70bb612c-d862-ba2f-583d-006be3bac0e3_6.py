from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 4.0
cavity_depth = 20.0
fillet_radius = 2.0
mount_hole_dia = 4.0
mount_hole_offset = 8.0

solid_body = Box(block_length, block_width, block_height)
solid_body = fillet(solid_body.edges(), fillet_radius)

cavity = Pos(0, 0, block_height - cavity_depth / 2) * Box(block_length - 2 * wall_thickness, block_width - 2 * wall_thickness, cavity_depth)
solid_body = solid_body - cavity

hole_x1 = -block_length / 2 + mount_hole_offset
hole_x2 = block_length / 2 - mount_hole_offset
hole_z = block_height / 2

hole1 = Pos(hole_x1, 0, hole_z) * Rot(90, 0, 0) * Cylinder(mount_hole_dia / 2, block_width)
hole2 = Pos(hole_x2, 0, hole_z) * Rot(90, 0, 0) * Cylinder(mount_hole_dia / 2, block_width)
solid_body = solid_body - hole1 - hole2

part = solid_body
part.name = "block_with_cavity_and_mount_holes"
export_step(part, "output.step")
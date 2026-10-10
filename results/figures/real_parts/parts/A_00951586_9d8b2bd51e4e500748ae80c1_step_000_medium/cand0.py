from build123d import *

block_size = 80.0
hole_diameter = 28.0
counterbore_diameter = 40.0
counterbore_depth = 10.0
chamfer_size = 8.0
rib_thickness = 5.0
rib_height = 20.0

solid_body = Box(block_size, block_size, block_size)
solid_body = chamfer(solid_body.edges(), chamfer_size)

hole_r = hole_diameter / 2
cbore_r = counterbore_diameter / 2

# X-axis holes
solid_body = solid_body - Rot(0, 90, 0) * Cylinder(hole_r, block_size)
solid_body = solid_body - Pos(block_size/2 - counterbore_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(cbore_r, counterbore_depth)
solid_body = solid_body - Pos(-block_size/2 + counterbore_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(cbore_r, counterbore_depth)

# Y-axis holes
solid_body = solid_body - Rot(90, 0, 0) * Cylinder(hole_r, block_size)
solid_body = solid_body - Pos(0, block_size/2 - counterbore_depth/2, 0) * Rot(90, 0, 0) * Cylinder(cbore_r, counterbore_depth)
solid_body = solid_body - Pos(0, -block_size/2 + counterbore_depth/2, 0) * Rot(90, 0, 0) * Cylinder(cbore_r, counterbore_depth)

# Z-axis holes
solid_body = solid_body - Cylinder(hole_r, block_size)
solid_body = solid_body - Pos(0, 0, block_size/2 - counterbore_depth/2) * Cylinder(cbore_r, counterbore_depth)
solid_body = solid_body - Pos(0, 0, -block_size/2 + counterbore_depth/2) * Cylinder(cbore_r, counterbore_depth)

rib = Pos(block_size/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "chamfered_block_with_holes_and_rib"
export_step(part, "output.step")
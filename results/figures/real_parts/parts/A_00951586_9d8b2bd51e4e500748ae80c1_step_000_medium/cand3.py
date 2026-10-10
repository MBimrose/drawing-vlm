from build123d import *

outer_size = 80.0
wall_thickness = 5.0
bore_diameter = 28.0
counterbore_diameter = 40.0
counterbore_depth = 10.0
chamfer_size = 8.0

solid_body = Box(outer_size, outer_size, outer_size)
solid_body = chamfer(solid_body.edges(), chamfer_size)

bore_r = bore_diameter / 2
cbore_r = counterbore_diameter / 2
half = outer_size / 2

solid_body = solid_body - Cylinder(bore_r, outer_size)
solid_body = solid_body - Pos(0, 0, half - counterbore_depth/2) * Cylinder(cbore_r, counterbore_depth)
solid_body = solid_body - Pos(0, 0, -half + counterbore_depth/2) * Cylinder(cbore_r, counterbore_depth)
solid_body = solid_body - Rot(0, 90, 0) * Cylinder(bore_r, outer_size)
solid_body = solid_body - Pos(half - counterbore_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(cbore_r, counterbore_depth)
solid_body = solid_body - Pos(-half + counterbore_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(cbore_r, counterbore_depth)
solid_body = solid_body - Rot(90, 0, 0) * Cylinder(bore_r, outer_size)
solid_body = solid_body - Pos(0, half - counterbore_depth/2, 0) * Rot(90, 0, 0) * Cylinder(cbore_r, counterbore_depth)
solid_body = solid_body - Pos(0, -half + counterbore_depth/2, 0) * Rot(90, 0, 0) * Cylinder(cbore_r, counterbore_depth)

part = solid_body
part.name = "cross_bore_block"
export_step(part, "output.step")
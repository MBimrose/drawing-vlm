from build123d import *

outer_size = 80.0
wall_thickness = 5.0
hole_diameter = 28.0
counterbore_diameter = 40.0
counterbore_depth = 10.0
chamfer_size = 8.0

solid = Box(outer_size, outer_size, outer_size)
solid = chamfer(solid.edges(), chamfer_size)

hole_r = hole_diameter / 2
cbore_r = counterbore_diameter / 2
half = outer_size / 2

solid = solid - Rot(0, 90, 0) * Cylinder(hole_r, outer_size)
solid = solid - Rot(0, 90, 0) * Pos(half - counterbore_depth/2, 0, 0) * Cylinder(cbore_r, counterbore_depth)
solid = solid - Rot(0, 90, 0) * Pos(-half + counterbore_depth/2, 0, 0) * Cylinder(cbore_r, counterbore_depth)

solid = solid - Rot(90, 0, 0) * Cylinder(hole_r, outer_size)
solid = solid - Rot(90, 0, 0) * Pos(0, half - counterbore_depth/2, 0) * Cylinder(cbore_r, counterbore_depth)
solid = solid - Rot(90, 0, 0) * Pos(0, -half + counterbore_depth/2, 0) * Cylinder(cbore_r, counterbore_depth)

solid = solid - Cylinder(hole_r, outer_size)
solid = solid - Pos(0, 0, half - counterbore_depth/2) * Cylinder(cbore_r, counterbore_depth)
solid = solid - Pos(0, 0, -half + counterbore_depth/2) * Cylinder(cbore_r, counterbore_depth)

part = solid
part.name = "cross_counterbore"
export_step(part, "output.step")
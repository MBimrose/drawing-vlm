from build123d import *

outer_width = 60.0
outer_depth = 40.0
outer_height = 40.0
wall_thickness = 8.0
cavity_width = outer_width - 2 * wall_thickness
cavity_depth = outer_depth - 2 * wall_thickness
hole_diameter = 12.0
counterbore_diameter = 20.0
counterbore_depth = 10.0
hole_offset_z = 20.0
chamfer_size = 1.0

solid_body = Box(outer_width, outer_depth, outer_height)
solid_body = solid_body - Box(cavity_width, cavity_depth, outer_height)

cbore = Pos(-outer_width/2 + counterbore_depth/2, 0, hole_offset_z) * Rot(0, 90, 0) * Cylinder(counterbore_diameter/2, counterbore_depth)
shaft = Pos(0, 0, hole_offset_z) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, outer_width + 10)
solid_body = solid_body - cbore - shaft

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "XMountSocket"
export_step(part, "output.step")
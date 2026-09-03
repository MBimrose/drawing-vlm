from build123d import *
import math

outer_width = 60.0
outer_depth = 40.0
outer_height = 40.0
wall_thickness = 8.0
inner_width = outer_width - 2 * wall_thickness
inner_depth = outer_depth - 2 * wall_thickness
chamfer_size = 1.0
counterbore_diameter = 12.0
counterbore_depth = 6.0
through_hole_diameter = 6.0
hole_center_y = 0.0
hole_center_z = outer_height * 0.6

outer_box = Box(outer_width, outer_depth, outer_height)
inner_box = Box(inner_width, inner_depth, outer_height)
socket_body = outer_box - inner_box

vertical_edges = socket_body.edges().filter_by(Axis.Z)
socket_body = chamfer(vertical_edges, chamfer_size)

cbore_cyl = Pos(-outer_width/2 + counterbore_depth/2, 0, hole_center_z) * Rot(0, 90, 0) * Cylinder(counterbore_diameter/2, counterbore_depth)
through_cyl = Pos(0, 0, hole_center_z) * Rot(0, 90, 0) * Cylinder(through_hole_diameter/2, outer_width + 20)

socket_body = socket_body - cbore_cyl
socket_body = socket_body - through_cyl

part = socket_body
part.name = "XMountSocket"
export_step(part, "output.step")
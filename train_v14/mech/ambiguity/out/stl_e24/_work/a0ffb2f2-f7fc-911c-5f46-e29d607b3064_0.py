from build123d import *

shank_diameter = 10.0
shank_length = 55.0
head_diameter = 30.0
head_height = 10.0
fillet_radius = 2.0
thread_diameter = 8.0
thread_depth = 15.0
chamfer_distance = 1.0

shank = Pos(0, 0, shank_length/2) * Cylinder(shank_diameter/2, shank_length)
head = Pos(0, 0, shank_length + head_height/2) * Cylinder(head_diameter/2, head_height)
solid_body = shank + head

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = fillet(top_edges, fillet_radius)

hole = Pos(0, 0, shank_length + head_height - thread_depth/2) * Cylinder(thread_diameter/2, thread_depth)
solid_body = solid_body - hole

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "pin_with_head"
export_step(part, "output.step")
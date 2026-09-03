from build123d import *

head_diameter = 30.0
head_height = 10.0
shank_diameter = 10.0
shank_length = 50.0
thread_diameter = 8.0
thread_length = 20.0
set_screw_diameter = 4.0
set_screw_depth = 6.0
set_screw_offset = 15.0
chamfer_size = 1.0
relief_width = 6.0
relief_depth = 2.0
relief_offset = 15.0

shank = Pos(0, 0, shank_length/2) * Cylinder(shank_diameter/2, shank_length)
head = Pos(0, 0, shank_length + head_height/2) * Cylinder(head_diameter/2, head_height)
result = shank + head

thread_hole = Pos(0, 0, shank_length + head_height - thread_length/2) * Cylinder(thread_diameter/2, thread_length)
result = result - thread_hole

set_screw_hole = Pos(shank_diameter/2 - set_screw_depth/2, 0, set_screw_offset) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
result = result - set_screw_hole

relief = Pos(0, 0, shank_length + head_height - relief_depth/2) * Box(relief_width, relief_depth, relief_depth)
result = result - relief

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "pin_with_head"
export_step(part, "output.step")
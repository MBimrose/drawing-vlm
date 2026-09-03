from build123d import *

main_pipe_length = 80.0
branch_pipe_length = 50.0
pipe_outer_diameter = 20.0
pipe_wall_thickness = 2.0
gusset_width = 15.0
gusset_length = 30.0
gusset_thickness = 4.0
hole_diameter = 4.0
hole_offset_from_center = 10.0

main_pipe = Pos(0, 0, main_pipe_length/2) * Cylinder(pipe_outer_diameter/2, main_pipe_length)
branch_pipe = Pos(branch_pipe_length/2, 0, main_pipe_length/2) * Rot(0, 90, 0) * Cylinder(pipe_outer_diameter/2, branch_pipe_length)
tee_body = main_pipe + branch_pipe
gusset = Pos(0, 0, gusset_thickness/2) * Box(gusset_width, gusset_length, gusset_thickness)
tee_with_gusset = tee_body + gusset
hole = Pos(hole_offset_from_center, 0, main_pipe_length/2) * Cylinder(hole_diameter/2, main_pipe_length)
part = tee_with_gusset - hole
part.name = "tee_pipe_with_gusset"
export_step(part, "output.step")
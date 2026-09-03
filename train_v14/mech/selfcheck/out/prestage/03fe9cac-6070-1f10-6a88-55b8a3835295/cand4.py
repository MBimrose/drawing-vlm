from build123d import *

main_pipe_length = 80.0
branch_pipe_length = 60.0
pipe_outer_diameter = 20.0
pipe_outer_radius = pipe_outer_diameter / 2.0
pipe_wall_thickness = 2.0
fillet_radius = 1.0
gusset_width = 30.0
gusset_height = 15.0
gusset_thickness = 4.0
hole_diameter = 4.0
hole_spacing = 20.0

main_pipe = Pos(0, 0, main_pipe_length/2) * Cylinder(pipe_outer_radius, main_pipe_length)
branch_pipe = Pos(branch_pipe_length/2, 0, main_pipe_length/2) * Rot(0, 90, 0) * Cylinder(pipe_outer_radius, branch_pipe_length)
tee = main_pipe + branch_pipe

gusset = Pos(0, 0, gusset_thickness/2) * Box(gusset_height, gusset_width, gusset_thickness)
tee = tee + gusset

hole_positions = [
    (branch_pipe_length/2 - hole_spacing, 0),
    (branch_pipe_length/2, 0),
    (branch_pipe_length/2 + hole_spacing, 0)
]
for x, y in hole_positions:
    tee = tee - Pos(x, y, main_pipe_length/2) * Cylinder(hole_diameter/2, main_pipe_length)

part = tee
part.name = "pipe_tee_with_gusset"
export_step(part, "output.step")
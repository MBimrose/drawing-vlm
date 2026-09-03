from build123d import *

main_pipe_length = 80.0
branch_pipe_length = 60.0
pipe_outer_diameter = 20.0
pipe_wall_thickness = 2.0
gusset_plate_width = 30.0
gusset_plate_height = 30.0
gusset_plate_thickness = 4.0
hole_diameter = 4.0
hole_offset = 15.0
chamfer_size = 2.0

main_pipe = Pos(0, 0, main_pipe_length / 2) * Cylinder(pipe_outer_diameter / 2, main_pipe_length)
branch_pipe = Pos(branch_pipe_length / 2, 0, main_pipe_length / 2) * Rot(0, 90, 0) * Cylinder(pipe_outer_diameter / 2, branch_pipe_length)
tee = main_pipe + branch_pipe

gusset = Pos(0, 0, gusset_plate_thickness / 2) * Box(gusset_plate_width, gusset_plate_height, gusset_plate_thickness)
for x, y in [(hole_offset, 0), (-hole_offset, 0), (0, hole_offset), (0, -hole_offset)]:
    gusset = gusset - Pos(x, y, gusset_plate_thickness / 2) * Cylinder(hole_diameter / 2, gusset_plate_thickness)

part = tee + gusset
part.name = "tee_with_gusset"
export_step(part, "output.step")
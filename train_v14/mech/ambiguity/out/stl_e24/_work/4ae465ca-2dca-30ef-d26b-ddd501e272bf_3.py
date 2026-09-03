from build123d import *

main_pipe_length = 80.0
branch_pipe_length = 50.0
pipe_outer_diameter = 30.0
pipe_wall_thickness = 2.0
collar_thickness = 3.0
collar_length = 20.0
mount_hole_diameter = 5.0
mount_hole_spacing = 25.0

pipe_outer_radius = pipe_outer_diameter / 2.0
pipe_inner_radius = pipe_outer_radius - pipe_wall_thickness
collar_outer_radius = pipe_outer_radius + collar_thickness

main_outer = Cylinder(pipe_outer_radius, main_pipe_length)
main_inner = Cylinder(pipe_inner_radius, main_pipe_length)
main_pipe = main_outer - main_inner

branch_outer = Pos(0, 0, main_pipe_length / 2.0) * Rot(0, 90, 0) * Cylinder(pipe_outer_radius, branch_pipe_length)
branch_inner = Pos(0, 0, main_pipe_length / 2.0) * Rot(0, 90, 0) * Cylinder(pipe_inner_radius, branch_pipe_length)
branch_pipe = branch_outer - branch_inner

tee = main_pipe + branch_pipe

collar = Pos(0, 0, collar_length / 2.0) * Cylinder(collar_outer_radius, collar_length)
tee_with_collar = tee + collar

hole1 = Pos(-mount_hole_spacing / 2.0, 0, main_pipe_length / 2.0 + pipe_outer_radius) * Cylinder(mount_hole_diameter / 2.0, pipe_wall_thickness * 2.0)
hole2 = Pos(mount_hole_spacing / 2.0, 0, main_pipe_length / 2.0 + pipe_outer_radius) * Cylinder(mount_hole_diameter / 2.0, pipe_wall_thickness * 2.0)

result = tee_with_collar - hole1 - hole2

part = result
part.name = "pipe_tee"
export_step(part, "output.step")
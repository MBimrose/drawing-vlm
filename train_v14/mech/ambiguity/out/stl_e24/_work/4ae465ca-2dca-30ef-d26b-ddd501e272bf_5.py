from build123d import *

main_length = 80.0
branch_length = 50.0
pipe_outer_dia = 30.0
pipe_wall_thk = 2.0
collar_length = 20.0
collar_extra_dia = 4.0
hole_dia = 5.0
hole_spacing = 30.0
chamfer_size = 0.5

pipe_outer_radius = pipe_outer_dia / 2.0
pipe_inner_radius = pipe_outer_radius - pipe_wall_thk
collar_outer_radius = pipe_outer_radius + collar_extra_dia / 2.0

main_outer = Cylinder(pipe_outer_radius, main_length)
branch_outer = Pos(0, 0, main_length / 2.0) * Rot(0, 90, 0) * Cylinder(pipe_outer_radius, branch_length)
tee_outer = main_outer + branch_outer

main_inner = Cylinder(pipe_inner_radius, main_length)
branch_inner = Pos(0, 0, main_length / 2.0) * Rot(0, 90, 0) * Cylinder(pipe_inner_radius, branch_length)
tee_hollow = tee_outer - main_inner - branch_inner

collar = Cylinder(collar_outer_radius, collar_length) - Cylinder(pipe_inner_radius, collar_length)
tee_with_collar = tee_hollow + collar

hole1 = Pos(-hole_spacing / 2.0, 0, main_length / 2.0) * Cylinder(hole_dia / 2.0, pipe_outer_dia * 2)
hole2 = Pos(hole_spacing / 2.0, 0, main_length / 2.0) * Cylinder(hole_dia / 2.0, pipe_outer_dia * 2)
tee_with_holes = tee_with_collar - hole1 - hole2

part = tee_with_holes
part.name = "pipe_tee"
export_step(part, "output.step")
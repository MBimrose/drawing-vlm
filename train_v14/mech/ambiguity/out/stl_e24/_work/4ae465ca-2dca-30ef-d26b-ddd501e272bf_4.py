from build123d import *

main_pipe_length = 80.0
branch_pipe_length = 50.0
outer_diameter = 30.0
wall_thickness = 2.0
inner_diameter = outer_diameter - 2 * wall_thickness
rib_height = 2.8
rib_width = 20.0
rib_position = 40.0
mount_hole_diameter = 5.0
mount_hole_offset = 12.0
keyway_width = 6.0
keyway_depth = 1.5
keyway_length = 30.0
pocket_width = 20.0
pocket_depth = 1.0
pocket_length = 15.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

main_outer = Cylinder(outer_radius, main_pipe_length)
branch_outer = Pos(0, 0, main_pipe_length / 2.0) * Rot(0, 90, 0) * Cylinder(outer_radius, branch_pipe_length)
tee_outer = main_outer + branch_outer

main_inner = Cylinder(inner_radius, main_pipe_length)
branch_inner = Pos(0, 0, main_pipe_length / 2.0) * Rot(0, 90, 0) * Cylinder(inner_radius, branch_pipe_length)
tee_hollow = tee_outer - main_inner - branch_inner

rib = Pos(0, 0, rib_position - main_pipe_length / 2.0) * Cylinder(outer_radius + rib_height, rib_width)
tee_with_rib = tee_hollow + rib

hole1 = Pos(mount_hole_offset, 0, main_pipe_length / 2.0) * Cylinder(mount_hole_diameter / 2.0, 200.0)
hole2 = Pos(-mount_hole_offset, 0, main_pipe_length / 2.0) * Cylinder(mount_hole_diameter / 2.0, 200.0)
tee_with_holes = tee_with_rib - hole1 - hole2

keyway = Pos(0, 0, main_pipe_length / 2.0 - keyway_depth / 2.0) * Box(keyway_length, keyway_width, keyway_depth)
tee_with_keyway = tee_with_holes - keyway

pocket = Pos(0, 0, main_pipe_length / 2.0 + outer_radius - pocket_depth / 2.0) * Box(pocket_length, pocket_width, pocket_depth)
part = tee_with_keyway - pocket
part.name = "tee_pipe"
export_step(part, "output.step")
from build123d import *

main_pipe_length = 80.0
branch_pipe_length = 60.0
pipe_outer_diameter = 20.0
pipe_wall_thickness = 2.0
mount_plate_width = 30.0
mount_plate_height = 15.0
mount_plate_thickness = 4.0
mount_hole_diameter = 4.0
mount_hole_spacing = 20.0

main_pipe = Pos(0, 0, main_pipe_length / 2) * Cylinder(pipe_outer_diameter / 2, main_pipe_length)
branch_pipe = Pos(branch_pipe_length / 2, 0, main_pipe_length / 2) * Rot(0, 90, 0) * Cylinder(pipe_outer_diameter / 2, branch_pipe_length)
tee_body = main_pipe + branch_pipe

plate = Pos(0, 0, -mount_plate_thickness / 2) * Box(mount_plate_height, mount_plate_width, mount_plate_thickness)
hole1 = Pos(-mount_hole_spacing / 2, 0, -mount_plate_thickness / 2) * Cylinder(mount_hole_diameter / 2, mount_plate_thickness + 1)
hole2 = Pos(mount_hole_spacing / 2, 0, -mount_plate_thickness / 2) * Cylinder(mount_hole_diameter / 2, mount_plate_thickness + 1)
plate_with_holes = plate - hole1 - hole2

part = tee_body + plate_with_holes
part.name = "tee_fitting_with_mount_plate"
export_step(part, "output.step")
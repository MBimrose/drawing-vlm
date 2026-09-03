from build123d import *

pipe_diameter = 20
main_length = 80
branch_length = 60
plate_width = 30
plate_depth = 15
plate_thickness = 4
hole_diameter = 4
hole_offset = 10

main_pipe = Pos(0, 0, main_length/2) * Cylinder(pipe_diameter/2, main_length)
branch_pipe = Pos(branch_length/2, 0, main_length/2) * Rot(0, 90, 0) * Cylinder(pipe_diameter/2, branch_length)
tee = main_pipe + branch_pipe

plate = Pos(0, 0, plate_thickness/2) * Box(plate_depth, plate_width, plate_thickness)
hole = Pos(hole_offset, 0, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)
plate_with_hole = plate - hole

part = tee + plate_with_hole
part.name = "tee_with_plate"
export_step(part, "output.step")
from build123d import *

main_diameter = 20.0
branch_diameter = 20.0
main_length = 80.0
branch_length = 60.0
pad_width = 30.0
pad_height = 12.0
pad_thickness = 4.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_count = 3

main_pipe = Cylinder(main_diameter / 2, main_length)
branch_pipe = Pos(branch_length / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(branch_diameter / 2, branch_length)
tee = main_pipe + branch_pipe

pad = Pos(0, 0, -main_length / 2 + pad_thickness / 2) * Box(pad_height, pad_width, pad_thickness)
tee_with_pad = tee + pad

start_x = -((hole_count - 1) * hole_spacing) / 2
result = tee_with_pad
for i in range(hole_count):
    x = start_x + i * hole_spacing
    hole = Pos(x, 0, 0) * Cylinder(hole_diameter / 2, main_length + 20)
    result = result - hole

part = result
part.name = "tee_with_pad_and_holes"
export_step(part, "output.step")
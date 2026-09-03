from build123d import *

main_pipe_length = 80.0
branch_pipe_length = 50.0
outer_diameter = 30.0
wall_thickness = 2.0
collar_thickness = 2.0
collar_width = 20.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_rows = 2
hole_columns = 3

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
collar_outer_radius = outer_radius + collar_thickness

main_outer = Cylinder(outer_radius, main_pipe_length)
branch_outer = Pos(0, 0, main_pipe_length/2) * Rot(0, 90, 0) * Cylinder(outer_radius, branch_pipe_length)
tee_outer = main_outer + branch_outer

main_inner = Cylinder(inner_radius, main_pipe_length)
branch_inner = Pos(0, 0, main_pipe_length/2) * Rot(0, 90, 0) * Cylinder(inner_radius, branch_pipe_length)
tee_hollow = tee_outer - main_inner - branch_inner

collar = Cylinder(collar_outer_radius, collar_width) - Cylinder(outer_radius, collar_width)
tee_with_collar = tee_hollow + collar

hole_positions = [
    ((i - (hole_columns - 1) / 2) * hole_spacing,
     (j - (hole_rows - 1) / 2) * hole_spacing)
    for i in range(hole_columns)
    for j in range(hole_rows)
]

result = tee_with_collar
for x, y in hole_positions:
    result = result - Pos(x, y, main_pipe_length/2 + branch_pipe_length/2) * Cylinder(hole_diameter/2, 100)

part = result
part.name = "pipe_tee"
export_step(part, "output.step")
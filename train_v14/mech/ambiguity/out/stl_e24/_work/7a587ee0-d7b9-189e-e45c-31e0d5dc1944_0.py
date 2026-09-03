from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - 2 * wall_thickness

outer_box = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
inner_box = Pos(0, 0, wall_thickness + inner_height / 2) * Box(inner_length, inner_width, inner_height)
part = outer_box - inner_box
part.name = "hollow_box"
export_step(part, "output.step")
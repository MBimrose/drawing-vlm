from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
base_thickness = 4.0

outer = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
inner = Pos(0, 0, base_thickness + (outer_height - base_thickness)/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, outer_height - base_thickness)
part = outer - inner
part.name = "hollow_box"
export_step(part, "output.step")
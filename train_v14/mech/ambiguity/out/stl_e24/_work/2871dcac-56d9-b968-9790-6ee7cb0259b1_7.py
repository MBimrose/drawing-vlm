from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 20.0
wall_thickness = 5.0
inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness
outer_fillet_radius = 4.0
inner_fillet_radius = 3.0

outer_box = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
outer_box = fillet(outer_box.edges().filter_by(Axis.Z), outer_fillet_radius)

inner_box = Pos(0, 0, wall_thickness + inner_height/2) * Box(inner_length, inner_width, inner_height)
inner_box = fillet(inner_box.edges().filter_by(Axis.Z), inner_fillet_radius)

part = outer_box - inner_box
part.name = "hollow_box"
export_step(part, "output.step")
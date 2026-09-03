from build123d import *

bar_radius = 5.0
bar_length = 60.0
tab_width = 12.0
tab_height = 8.0
tab_thickness = 4.0
hole_diameter = 6.0
hole_depth = 35.0
chamfer_size = 0.5

bar = Pos(bar_length/2, 0, 0) * Rot(0, 90, 0) * Cylinder(bar_radius, bar_length)
tab = Pos(bar_length, 0, 0) * Box(tab_thickness, tab_width, tab_height)
result = bar + tab

hole = Pos(bar_length - hole_depth/2, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
result = result - hole

x_edges = result.edges().filter_by(Axis.X)
result = chamfer(x_edges, chamfer_size)

part = result
part.name = "bar_with_tab_and_hole"
export_step(part, "output.step")
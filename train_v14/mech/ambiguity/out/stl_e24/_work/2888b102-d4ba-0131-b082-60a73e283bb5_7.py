from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 12.0
wall_thickness = 4.0
tab_length = 20.0
tab_width = 8.0
hole_diameter = 6.0
hole_offset_x = 20.0
hole_offset_y = 10.0
chamfer_distance = 1.0

base = Box(bracket_length, bracket_width, bracket_thickness)
tab = Pos(bracket_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, bracket_thickness)
combined = base + tab

inner_cut = Box(bracket_length - 2*wall_thickness, bracket_width - 2*wall_thickness, bracket_thickness)
result = combined - inner_cut

hole = Pos(-bracket_length/2 + hole_offset_x, -bracket_width/2 + hole_offset_y, 0) * Cylinder(hole_diameter/2, bracket_thickness)
result = result - hole

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_distance)

part = result
part.name = "bracket"
export_step(part, "output.step")
from build123d import *

bracket_length = 80.0
bracket_width = 50.0
bracket_thickness = 8.0
tab_length = 12.0
tab_width = 12.0
fillet_radius = 5.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 12.0
hole_rows = 4
hole_cols = 3
rib_height = 2.0
rib_margin = 5.0

base = Box(bracket_length, bracket_width, bracket_thickness)
tab = Pos(bracket_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, bracket_thickness)
result = base + tab

bottom_face = result.faces().sort_by(Axis.Z)[0]
bottom_x_edges = bottom_face.edges().filter_by(Axis.X)
result = fillet(bottom_x_edges, fillet_radius)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)

rib_cut = Pos(0, 0, bracket_thickness/2 - rib_height/2) * Box(bracket_length - 2*rib_margin, bracket_width - 2*rib_margin, rib_height)
result = result - rib_cut

part = result
part.name = "bracket_with_tab_and_holes"
export_step(part, "output.step")
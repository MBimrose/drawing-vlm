from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
wall_thickness = 2.0
tab_length = 12.0
tab_width = 12.0
tab_fillet_radius = 5.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 12.0
hole_rows = 4
hole_cols = 3

base = Box(plate_length, plate_width, plate_thickness)
tab = Pos(plate_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, plate_thickness)
solid_body = base + tab

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
tab_edges = bottom_face.edges().filter_by(Axis.X)
solid_body = fillet(tab_edges, tab_fillet_radius)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
pocket = Pos(0, 0, plate_thickness/2 - wall_thickness/2) * Box(plate_length - 2*wall_thickness, plate_width - 2*wall_thickness, wall_thickness)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

part = solid_body
part.name = "plate_with_tab_and_holes"
export_step(part, "output.step")
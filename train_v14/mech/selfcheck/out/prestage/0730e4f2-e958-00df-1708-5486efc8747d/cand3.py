from build123d import *

outer_width = 80.0
outer_height = 60.0
length = 40.0
wall_thickness = 2.0
notch_width = 20.0
notch_height = 15.0
fillet_radius = 3.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3

base = Box(outer_width, outer_height, length)
notch = Pos(outer_width/2 - notch_width/2, 0, 0) * Box(notch_width, notch_height, length)
solid_body = base - notch

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        z = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, outer_height/2, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, outer_height)
        solid_body = solid_body - hole

part = solid_body
part.name = "shelled_box_with_notch_and_holes"
export_step(part, "output.step")
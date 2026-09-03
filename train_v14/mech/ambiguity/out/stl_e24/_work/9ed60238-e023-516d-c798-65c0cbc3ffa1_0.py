from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
corner_fillet_radius = 5.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 12.0
hole_rows = 4
hole_cols = 3
tab_width = 12.0
tab_length = 15.0
tab_chamfer = 0.5
pocket_depth = 2.0
pocket_margin = 2.0

solid_body = Box(plate_length, plate_width, plate_thickness)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_x_edges = bottom_face.edges().filter_by(Axis.X)
solid_body = fillet(bottom_x_edges, corner_fillet_radius)

tab = Pos(plate_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, plate_thickness)
solid_body = solid_body + tab

tab_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
solid_body = chamfer(tab_edges, tab_chamfer)

pocket_w = plate_length - 2 * pocket_margin
pocket_h = plate_width - 2 * pocket_margin
pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)
        solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_tab_pocket_and_holes"
export_step(part, "output.step")
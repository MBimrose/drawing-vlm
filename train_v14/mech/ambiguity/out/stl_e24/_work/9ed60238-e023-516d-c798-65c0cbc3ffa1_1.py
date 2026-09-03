from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
fillet_radius = 5.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 12.0
hole_rows = 4
hole_cols = 3
tab_length = 12.0
tab_height = 10.0
tab_thickness = plate_thickness
rib_depth = 2.0
rib_offset = 2.0

solid_body = Box(plate_length, plate_width, plate_thickness)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges().filter_by(Axis.X)
solid_body = fillet(bottom_edges, fillet_radius)

tab = Pos(plate_length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_height, tab_thickness)
solid_body = solid_body + tab

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

rib_cut = Pos(0, 0, plate_thickness/2 - rib_depth/2) * Box(plate_length - 2*rib_offset, plate_width - 2*rib_offset, rib_depth)
solid_body = solid_body - rib_cut

part = solid_body
part.name = "plate_with_tab_holes_and_rib"
export_step(part, "output.step")
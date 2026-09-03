from build123d import *

cover_width = 80.0
cover_length = 60.0
cover_thickness = 8.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = 2.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 4
central_hole_diameter = 6.0
chamfer_size = 0.5

solid_body = Box(cover_width, cover_length, cover_thickness)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib1 = Pos(0, 0, wall_thickness + rib_height/2) * Box(cover_width - 2*wall_thickness, rib_thickness, rib_height)
rib2 = Pos(0, 0, wall_thickness + rib_height/2) * Box(rib_thickness, cover_length - 2*wall_thickness, rib_height)
solid_body = solid_body + rib1 + rib2

solid_body = solid_body - Cylinder(central_hole_diameter/2, cover_thickness + 10)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, cover_thickness + 10)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "cover_plate"
export_step(part, "output.step")
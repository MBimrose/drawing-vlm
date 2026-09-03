from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
rib_width = 6.0
rib_height = 5.0
fillet_radius = 1.5
hole_diameter = 3.0
hole_spacing_x = 15.0
hole_spacing_y = 20.0
hole_rows = 4
hole_cols = 3

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

rib_positions = [
    (-outer_length/2 + rib_width/2, -outer_width/2 + rib_width/2),
    ( outer_length/2 - rib_width/2, -outer_width/2 + rib_width/2),
    (-outer_length/2 + rib_width/2,  outer_width/2 - rib_width/2),
    ( outer_length/2 - rib_width/2,  outer_width/2 - rib_width/2),
]
for x, y in rib_positions:
    solid_body = solid_body + Pos(x, y, -rib_height/2) * Box(rib_width, rib_width, rib_height)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(hole_diameter/2, outer_height + 10)

part = solid_body
part.name = "hollow_box_with_ribs_and_holes"
export_step(part, "output.step")
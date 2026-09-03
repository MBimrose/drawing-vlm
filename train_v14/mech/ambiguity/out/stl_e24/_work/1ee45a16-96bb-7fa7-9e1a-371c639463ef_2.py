from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
rib_width = 6.0
rib_height = 5.0
rib_offset = 4.0
hole_diameter = 3.0
hole_spacing_x = 15.0
hole_spacing_y = 20.0
hole_rows = 4
hole_cols = 5
fillet_radius = 1.5

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
shelled = offset(base, amount=-wall_thickness, openings=[top_face])

rib = Box(rib_width, rib_width, rib_height)
rib_positions = [
    (-outer_length/2 + rib_offset + rib_width/2, -outer_width/2 + rib_offset + rib_width/2),
    ( outer_length/2 - rib_offset - rib_width/2, -outer_width/2 + rib_offset + rib_width/2),
    (-outer_length/2 + rib_offset + rib_width/2,  outer_width/2 - rib_offset - rib_width/2),
    ( outer_length/2 - rib_offset - rib_width/2,  outer_width/2 - rib_offset - rib_width/2),
]
ribs = Compound([Pos(x, y, -rib_height/2) * rib for x, y in rib_positions])
combined = shelled + ribs

hole = Cylinder(hole_diameter/2, outer_height + rib_height + 20)
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        combined = combined - Pos(x, y, outer_height/2) * hole

vertical_edges = combined.edges().filter_by(Axis.Z)
result = fillet(vertical_edges, fillet_radius)

part = result
part.name = "shelled_box_with_ribs_and_holes"
export_step(part, "output.step")
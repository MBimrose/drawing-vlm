from build123d import *

outer_width = 80.0
outer_depth = 60.0
outer_height = 40.0
wall_thickness = 2.0
fillet_radius = 3.0
notch_width = 20.0
notch_depth = 10.0
hole_diameter = 4.0
hole_rows = 2
hole_cols = 3
hole_spacing_x = 20.0
hole_spacing_y = 15.0

base = Box(outer_width, outer_depth, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

notch = Pos(outer_width/2 - notch_width/2, outer_depth/2 - notch_depth/2, 0) * Box(notch_width, notch_depth, outer_height)
base = base - notch

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        z = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, outer_depth/2, z) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, outer_depth + 10)
        base = base - hole

part = base
part.name = "hollow_box_with_notch_and_holes"
export_step(part, "output.step")
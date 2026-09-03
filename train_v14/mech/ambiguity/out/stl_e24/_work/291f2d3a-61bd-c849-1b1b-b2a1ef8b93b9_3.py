from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 8.0
wall_thickness = 2.0
rib_thickness = 2.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 4
central_hole_diameter = 6.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0
chamfer_size = 0.5

base = Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
shell_body = offset(base, amount=-wall_thickness, openings=[top_face])

rib1 = Box(outer_length - 2*wall_thickness, rib_thickness, wall_thickness)
rib2 = Box(rib_thickness, outer_width - 2*wall_thickness, wall_thickness)
shell_body = shell_body + rib1 + rib2

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        shell_body = shell_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, outer_height + 10)

shell_body = shell_body - Cylinder(central_hole_diameter/2, outer_height + 10)

pocket = Pos(0, 0, outer_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
shell_body = shell_body - pocket

vertical_edges = shell_body.edges().filter_by(Axis.Z)
shell_body = chamfer(vertical_edges, chamfer_size)

part = shell_body
part.name = "shelled_box_with_ribs_and_holes"
export_step(part, "output.step")
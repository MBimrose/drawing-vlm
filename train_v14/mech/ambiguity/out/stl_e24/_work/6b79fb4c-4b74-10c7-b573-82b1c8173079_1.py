from build123d import *

outer_width = 80.0
outer_height = 40.0
length = 100.0
wall_thickness = 5.0
chamfer_size = 2.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 3.0
clearance_hole_diameter = 8.0
hole_diameter = 3.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 3
hole_cols = 4

solid_body = Box(outer_width, length, outer_height)

inner_width = outer_width - wall_thickness
inner_height = outer_height - 2 * wall_thickness
inner_cut = Pos(wall_thickness / 2, 0, 0) * Box(inner_width, length, inner_height)
solid_body = solid_body - inner_cut

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

pocket = Pos(-outer_width/2 + pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

clearance_hole = Pos(-outer_width/2 + wall_thickness/2, 0, 0) * Rot(0, 90, 0) * Cylinder(clearance_hole_diameter/2, wall_thickness + 10)
solid_body = solid_body - clearance_hole

for i in range(hole_cols):
    for j in range(hole_rows):
        y = (i - (hole_cols - 1) / 2) * hole_spacing_x
        z = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(-outer_width/2 + wall_thickness/2, y, z) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, wall_thickness + 10)
        solid_body = solid_body - hole

part = solid_body
part.name = "c_channel_with_pocket_and_holes"
export_step(part, "output.step")
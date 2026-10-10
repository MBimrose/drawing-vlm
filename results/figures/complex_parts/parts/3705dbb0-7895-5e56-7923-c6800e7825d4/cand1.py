from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
chamfer_size = 0.5
vent_hole_diameter = 1.5
vent_spacing_x = 10.0
vent_spacing_y = 10.0
mount_hole_diameter = 3.0
pocket_margin = 4.0
pocket_depth = 4.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness

vent_cols = int(inner_length // vent_spacing_x)
vent_rows = int(inner_width // vent_spacing_y)

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

floor = Pos(0, 0, wall_thickness/2) * Box(inner_length, inner_width, wall_thickness)
solid_body = solid_body + floor

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols-1)/2) * vent_spacing_x
        y = (j - (vent_rows-1)/2) * vent_spacing_y
        solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(vent_hole_diameter/2, outer_height + 10)

solid_body = solid_body - Pos(-outer_length/2, 0, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length + 10)
solid_body = solid_body - Pos(outer_length/2, 0, outer_height/2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length + 10)

pocket_w = inner_length - 2 * pocket_margin
pocket_d = inner_width - 2 * pocket_margin
pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_w, pocket_d, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "ventilated_box"
export_step(part, "output.step")
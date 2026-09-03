from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
pocket_length = 40.0
pocket_width = 25.0
pocket_depth = 4.0
mount_hole_diameter = 3.0
mount_hole_offset = 5.0
vent_hole_diameter = 1.5
vent_hole_spacing = 10.0
vent_rows = 4
vent_cols = 7
chamfer_distance = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

solid_body = chamfer(solid_body.edges(), chamfer_distance)

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

mount_hole = Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, outer_length + 10)
solid_body = solid_body - Pos(outer_length/2, 0, outer_height/2) * mount_hole
solid_body = solid_body - Pos(-outer_length/2, 0, outer_height/2) * mount_hole

vent_hole = Cylinder(vent_hole_diameter/2, outer_height + 10)
for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols-1)/2) * vent_hole_spacing
        y = (j - (vent_rows-1)/2) * vent_hole_spacing
        solid_body = solid_body - Pos(x, y, outer_height/2) * vent_hole

part = solid_body
part.name = "ventilated_box"
export_step(part, "output.step")
from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_width = 4.0
vent_slot_height = 10.0
vent_spacing_x = 8.0
vent_spacing_y = 12.0
vent_rows = 3
vent_cols = 4
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
chamfer_distance = 1.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols-1)/2) * vent_spacing_x
        y = (j - (vent_rows-1)/2) * vent_spacing_y
        vent = Pos(x, y, outer_height - wall_thickness/2) * Box(vent_slot_width, vent_slot_height, wall_thickness)
        solid_body = solid_body - vent

mount_points = [
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
    (-outer_length/2 + mount_hole_offset,  outer_width/2 - mount_hole_offset),
    ( outer_length/2 - mount_hole_offset,  outer_width/2 - mount_hole_offset),
]
for x, y in mount_points:
    hole = Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "vented_box"
export_step(part, "output.step")
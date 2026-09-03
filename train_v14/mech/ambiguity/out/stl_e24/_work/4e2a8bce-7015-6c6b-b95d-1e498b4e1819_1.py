from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
lid_thickness = 2.0
vent_slot_width = 4.0
vent_slot_height = 10.0
vent_spacing_x = 8.0
vent_spacing_y = 12.0
vent_rows = 3
vent_cols = 5
mount_hole_dia = 2.0
mount_hole_offset = 5.0
chamfer_size = 0.5

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

vent_points = [
    ((i - (vent_cols - 1) / 2) * vent_spacing_x,
     (j - (vent_rows - 1) / 2) * vent_spacing_y)
    for i in range(vent_cols) for j in range(vent_rows)
]
for x, y in vent_points:
    base = base - Pos(x, y, outer_height - wall_thickness/2) * Box(vent_slot_width, vent_slot_height, wall_thickness)

mount_points = [
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset,  outer_width/2 - mount_hole_offset),
    (-outer_length/2 + mount_hole_offset,  outer_width/2 - mount_hole_offset)
]
for x, y in mount_points:
    base = base - Pos(x, y, outer_height/2) * Cylinder(mount_hole_dia/2, outer_height + 10)

bottom_face = base.faces().sort_by(Axis.Z)[0]
base = chamfer(bottom_face.edges(), chamfer_size)

lid = Pos(0, 0, outer_height + lid_thickness/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, lid_thickness)
part = base + lid
part.name = "ventilated_box_with_lid"
export_step(part, "output.step")
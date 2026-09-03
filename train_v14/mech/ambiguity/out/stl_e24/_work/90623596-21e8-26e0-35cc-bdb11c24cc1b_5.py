from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_width = 5.0
vent_slot_height = 12.0
vent_spacing_x = 12.0
vent_spacing_y = 10.0
vent_rows = 2
vent_cols = 3
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
chamfer_size = 0.5

solid_body = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols - 1) / 2) * vent_spacing_x
        y = (j - (vent_rows - 1) / 2) * vent_spacing_y
        vent = Pos(x, y, outer_height - wall_thickness / 2) * Box(vent_slot_width, vent_slot_height, wall_thickness)
        solid_body = solid_body - vent

mount_hole = Pos(outer_length / 2, 0, outer_height / 2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, outer_length)
solid_body = solid_body - mount_hole

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "vented_box"
export_step(part, "output.step")
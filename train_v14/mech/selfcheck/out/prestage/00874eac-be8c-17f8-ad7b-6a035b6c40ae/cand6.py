from build123d import *

outer_width = 80.0
outer_depth = 60.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_width = 5.0
vent_slot_height = 12.0
vent_rows = 3
vent_cols = 4
vent_spacing_x = 12.0
vent_spacing_y = 15.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
chamfer_size = 1.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols-1)/2) * vent_spacing_x
        y = (j - (vent_rows-1)/2) * vent_spacing_y
        solid_body = solid_body - Pos(x, y, outer_height - wall_thickness/2) * Box(vent_slot_width, vent_slot_height, wall_thickness)

for x, y in [(-outer_width/2 + mount_hole_offset, -outer_depth/2 + mount_hole_offset),
             (outer_width/2 - mount_hole_offset, -outer_depth/2 + mount_hole_offset),
             (-outer_width/2 + mount_hole_offset, outer_depth/2 - mount_hole_offset),
             (outer_width/2 - mount_hole_offset, outer_depth/2 - mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)

part = solid_body
part.name = "ventilated_enclosure"
export_step(part, "output.step")
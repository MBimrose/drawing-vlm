from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_length = 50.0
vent_slot_height = 10.0
mount_hole_diameter = 4.0
mount_hole_spacing_x = 60.0
mount_hole_spacing_y = 30.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

vent_cut = Pos(0, -outer_width/2 + wall_thickness/2, outer_height/2) * Box(vent_slot_length, wall_thickness, vent_slot_height)
solid_body = solid_body - vent_cut

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)

part = solid_body
part.name = "vented_box_with_mount_holes"
export_step(part, "output.step")
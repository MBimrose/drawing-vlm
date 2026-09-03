from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_width = 30.0
vent_height = 15.0
vent_offset_y = 0.0
mount_hole_dia = 2.0
mount_hole_spacing_x = 70.0
mount_hole_spacing_y = 40.0
rib_thickness = 1.0
rib_height = 8.0
rib_width = 6.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

vent_cut = Pos(0, outer_width/2 - wall_thickness/2, outer_height/2 + vent_offset_y) * Box(vent_width, wall_thickness, vent_height)
solid_body = solid_body - vent_cut

for dx in [-mount_hole_spacing_x/2, mount_hole_spacing_x/2]:
    for dy in [-mount_hole_spacing_y/2, mount_hole_spacing_y/2]:
        hole = Pos(dx, dy, outer_height/2) * Cylinder(mount_hole_dia/2, outer_height)
        solid_body = solid_body - hole

rib1 = Pos(-outer_length/2 + wall_thickness + rib_width/2, 0, outer_height/2) * Box(rib_width, rib_thickness, rib_height)
rib2 = Pos(outer_length/2 - wall_thickness - rib_width/2, 0, outer_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "vented_box_with_ribs"
export_step(part, "output.step")
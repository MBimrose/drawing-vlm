from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
vent_slot_width = 30.0
vent_slot_height = 6.0
snap_tab_width = 10.0
snap_tab_height = 12.0
snap_tab_thickness = 1.0
fillet_radius = 1.0
mount_hole_dia = 2.0
mount_hole_spacing_x = 40.0
mount_hole_spacing_y = 25.0
pocket_depth = 0.8
pocket_width = 28.0
pocket_height = 6.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

vent_cut = Pos(outer_length/2 - wall_thickness/2, 0, outer_height/2) * Box(wall_thickness, vent_slot_width, vent_slot_height)
solid_body = solid_body - vent_cut

tab = Pos(outer_length/2 + snap_tab_thickness/2, 0, outer_height/2) * Box(snap_tab_thickness, snap_tab_width, snap_tab_height)
solid_body = solid_body + tab

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(mount_hole_dia/2, outer_height)

pocket = Pos(-outer_length/2 + pocket_depth/2, 0, outer_height/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

part = solid_body
part.name = "ventilated_box_with_tabs"
export_step(part, "output.step")
from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_width = 30.0
vent_slot_height = 5.0
mount_tab_width = 10.0
mount_tab_height = 5.0
mount_tab_thickness = 3.0
rib_thickness = 2.0
rib_height = 5.0
rib_spacing = 15.0
snap_fit_width = 12.0
snap_fit_height = 6.0
snap_fit_thickness = 2.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

vent_cut = Pos(0, 0, outer_height - wall_thickness/2) * Box(vent_slot_width, vent_slot_height, wall_thickness)
solid_body = solid_body - vent_cut

tab = Pos(0, outer_width/2 + mount_tab_thickness/2, outer_height/2 - mount_tab_height/2) * Box(mount_tab_width, mount_tab_thickness, mount_tab_height)
solid_body = solid_body + tab

rib = Pos(0, -outer_width/2 - rib_thickness/2, outer_height/2 - rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
solid_body = solid_body + rib

snap_cut = Pos(0, 0, outer_height - snap_fit_thickness/2) * Box(snap_fit_width, snap_fit_height, snap_fit_thickness)
solid_body = solid_body - snap_cut

part = solid_body
part.name = "ventilated_box_with_tabs"
export_step(part, "output.step")
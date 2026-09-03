from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
snap_tab_width = 10.0
snap_tab_height = 5.0
snap_tab_thickness = 3.0
snap_slot_width = 4.0
snap_slot_depth = 1.0
mount_hole_diameter = 2.0
mount_hole_spacing_x = 6.0
mount_hole_spacing_y = 8.0
rib_thickness = 1.5
rib_height = 5.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

tab = Pos(0, outer_width/2 + snap_tab_thickness/2, outer_height/2 - snap_tab_height/2 - 5) * Box(snap_tab_width, snap_tab_thickness, snap_tab_height)
solid_body = solid_body + tab

slot = Pos(0, outer_width/2 - snap_slot_depth/2, outer_height/2 - snap_tab_height/2 - 5) * Box(snap_tab_width, snap_slot_depth, snap_slot_width)
solid_body = solid_body - slot

for dx in [-mount_hole_spacing_x/2, mount_hole_spacing_x/2]:
    for dy in [-mount_hole_spacing_y/2, mount_hole_spacing_y/2]:
        hole = Pos(dx, outer_width/2 + snap_tab_thickness/2 + dy, outer_height/2 - snap_tab_height/2 - 5) * Cylinder(mount_hole_diameter/2, snap_tab_thickness + 10)
        solid_body = solid_body - hole

rib = Pos(0, -outer_width/2 - rib_thickness/2, outer_height/2 - rib_height/2 - 5) * Box(rib_thickness, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "snap_fit_box"
export_step(part, "output.step")
from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
snap_tab_width = 30.0
snap_tab_height = 10.0
snap_tab_thickness = 2.0
snap_notch_depth = 0.8
vent_slot_width = 4.0
vent_slot_height = 12.0
vent_slot_offset = 5.0
fillet_radius = 1.0
mount_hole_dia = 2.0
mount_hole_spacing_x = 60.0
mount_hole_spacing_y = 30.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

tab = Pos(outer_length/2, 0, outer_height/2) * Box(snap_tab_thickness, snap_tab_width, snap_tab_height)
solid_body = solid_body + tab

notch = Pos(outer_length/2 + snap_tab_thickness/2, 0, outer_height/2) * Box(snap_notch_depth, snap_tab_width - 2*wall_thickness, snap_tab_height - 2*wall_thickness)
solid_body = solid_body - notch

vent = Pos(-outer_length/2 + wall_thickness/2, 0, outer_height/2) * Box(wall_thickness, vent_slot_width, vent_slot_height)
solid_body = solid_body - vent

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    hole = Pos(x, y, outer_height/2) * Cylinder(mount_hole_dia/2, outer_height)
    solid_body = solid_body - hole

part = solid_body
part.name = "snap_fit_enclosure"
export_step(part, "output.step")
from build123d import *

enclosure_length = 80.0
enclosure_width = 50.0
enclosure_height = 20.0
wall_thickness = 2.0
vent_slot_width = 4.0
vent_slot_height = 12.0
vent_slot_offset_z = 0.0
snap_tab_thickness = 1.0
snap_tab_width = 30.0
snap_tab_height = 6.0
mount_hole_diameter = 3.0
mount_hole_spacing_x = 60.0
mount_hole_spacing_y = 30.0
top_fillet_radius = 1.0
pocket_depth = 5.0
pocket_margin = 5.0

solid_body = Pos(0, 0, enclosure_height/2) * Box(enclosure_length, enclosure_width, enclosure_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, top_fillet_radius)
vent_cut = Pos(-enclosure_length/2 + wall_thickness/2, 0, enclosure_height/2 + vent_slot_offset_z) * Box(wall_thickness, vent_slot_width, vent_slot_height)
solid_body = solid_body - vent_cut
snap_tab = Pos(enclosure_length/2 + snap_tab_thickness/2, 0, enclosure_height/2) * Box(snap_tab_thickness, snap_tab_width, snap_tab_height)
solid_body = solid_body + snap_tab
for dx in [-mount_hole_spacing_x/2, mount_hole_spacing_x/2]:
    for dy in [-mount_hole_spacing_y/2, mount_hole_spacing_y/2]:
        hole = Pos(dx, dy, enclosure_height/2) * Cylinder(mount_hole_diameter/2, enclosure_height + 10)
        solid_body = solid_body - hole
pocket = Pos(0, 0, enclosure_height - pocket_depth/2) * Box(enclosure_length - 2*pocket_margin, enclosure_width - 2*pocket_margin, pocket_depth)
solid_body = solid_body - pocket
part = solid_body
part.name = "enclosure"
export_step(part, "output.step")
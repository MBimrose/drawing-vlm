from build123d import *

enclosure_length = 80.0
enclosure_width = 50.0
enclosure_height = 20.0
wall_thickness = 2.0
vent_slot_width = 4.0
vent_slot_height = 12.0
snap_tab_width = 30.0
snap_tab_height = 12.0
snap_tab_thickness = 1.0
snap_tab_flex_depth = 0.8
fillet_radius = 1.0

base = Pos(0, 0, enclosure_height/2) * Box(enclosure_length, enclosure_width, enclosure_height)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[bottom_face])
vertical_edges = base.edges().filter_by(Axis.Z)
base = fillet(vertical_edges, fillet_radius)

vent_cut = Pos(-enclosure_length/2 + wall_thickness/2, 0, enclosure_height/2) * Box(wall_thickness, vent_slot_width, vent_slot_height)
base = base - vent_cut

snap_tab = Pos(enclosure_length/2 + snap_tab_thickness/2, 0, enclosure_height/2) * Box(snap_tab_thickness, snap_tab_width, snap_tab_height)
base = base + snap_tab

flex_cut = Pos(enclosure_length/2 + snap_tab_thickness - snap_tab_flex_depth/2, 0, enclosure_height/2) * Box(snap_tab_flex_depth, snap_tab_width - 2*snap_tab_flex_depth, snap_tab_height - 2*snap_tab_flex_depth)
base = base - flex_cut

part = base
part.name = "enclosure_with_vent_and_snap_tab"
export_step(part, "output.step")
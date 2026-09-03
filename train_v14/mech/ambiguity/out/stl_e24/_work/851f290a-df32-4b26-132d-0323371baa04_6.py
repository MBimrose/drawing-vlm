from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
snap_tab_width = 30.0
snap_tab_height = 6.0
snap_tab_thickness = 1.5
vent_slot_width = 10.0
vent_slot_height = 4.0
vent_slot_offset = 5.0
rib_thickness = 1.0
rib_height = 12.0
fillet_radius = 1.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[bottom_face])
vertical_edges = base.edges().filter_by(Axis.Z)
base = fillet(vertical_edges, fillet_radius)

snap_cut = Pos(outer_length/2 - snap_tab_thickness/2, 0, outer_height/2) * Box(snap_tab_thickness, snap_tab_width, snap_tab_height)
base = base - snap_cut

vent_cut = Pos(-outer_length/2 + wall_thickness/2, 0, outer_height/2 + vent_slot_offset) * Box(wall_thickness, vent_slot_width, vent_slot_height)
base = base - vent_cut

rib = Pos(outer_length/2 + rib_thickness/2, 0, outer_height/2) * Box(rib_thickness, rib_height, wall_thickness)
base = base + rib

part = base
part.name = "snap_fit_box"
export_step(part, "output.step")
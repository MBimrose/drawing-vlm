from build123d import *

cover_length = 80.0
cover_width = 60.0
cover_thickness = 12.0
wall_thickness = 4.0
snap_tab_length = 20.0
snap_tab_height = 6.0
snap_tab_thickness = 2.0
vent_slot_length = 30.0
vent_slot_width = 2.0
vent_spacing = 10.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
rib_thickness = 2.0
rib_height = 3.0
rib_spacing = 15.0
chamfer_distance = 0.5

outer = Box(cover_length, cover_width, cover_thickness)
inner = Pos(0, 0, -wall_thickness/2) * Box(cover_length - 2*wall_thickness, cover_width - 2*wall_thickness, cover_thickness - wall_thickness)
result = outer - inner

tab = Pos(0, cover_width/2 + snap_tab_thickness/2, 0) * Box(snap_tab_length, snap_tab_thickness, snap_tab_height)
result = result + tab

vent_count = int((cover_width - 2*wall_thickness) // vent_spacing)
for i in range(vent_count):
    y = -cover_width/2 + wall_thickness + vent_spacing/2 + i*vent_spacing
    result = result - Pos(0, y, cover_thickness/2 - wall_thickness/2) * Box(vent_slot_length, vent_slot_width, wall_thickness)

hole_positions = [
    (-cover_length/2 + mount_hole_offset, -cover_width/2 + mount_hole_offset),
    ( cover_length/2 - mount_hole_offset, -cover_width/2 + mount_hole_offset),
    (-cover_length/2 + mount_hole_offset,  cover_width/2 - mount_hole_offset),
    ( cover_length/2 - mount_hole_offset,  cover_width/2 - mount_hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, cover_thickness)

rib_count = int((cover_width - 2*wall_thickness) // rib_spacing)
for i in range(rib_count):
    y = -cover_width/2 + wall_thickness + rib_spacing/2 + i*rib_spacing
    result = result + Pos(0, y, -wall_thickness/2) * Box(cover_length - 2*wall_thickness, rib_thickness, rib_height)

tab_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:]
result = chamfer(tab_edges, chamfer_distance)

part = result
part.name = "cover_with_tabs_vents_ribs"
export_step(part, "output.step")
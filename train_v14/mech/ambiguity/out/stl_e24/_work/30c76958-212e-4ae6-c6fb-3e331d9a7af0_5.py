from build123d import *

cover_length = 80.0
cover_width = 60.0
cover_thickness = 12.0
wall_thickness = 4.0
snap_tab_width = 20.0
snap_tab_height = 6.0
snap_tab_thickness = 2.0
snap_fillet_radius = 0.5
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
rib_thickness = 2.0
rib_height = 3.0
rib_spacing = 15.0

base = Box(cover_length, cover_width, cover_thickness)
inner_cut = Pos(0, 0, -wall_thickness/2) * Box(cover_length - 2*wall_thickness, cover_width - 2*wall_thickness, cover_thickness - wall_thickness)
result = base - inner_cut

hole_positions = [
    (-cover_length/2 + mount_hole_offset, -cover_width/2 + mount_hole_offset),
    (cover_length/2 - mount_hole_offset, -cover_width/2 + mount_hole_offset),
    (-cover_length/2 + mount_hole_offset, cover_width/2 - mount_hole_offset),
    (cover_length/2 - mount_hole_offset, cover_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, cover_thickness)

num_ribs = int((cover_width - 2*wall_thickness) // rib_spacing)
for i in range(num_ribs):
    y_pos = -cover_width/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    result = result + Pos(0, y_pos, -rib_height/2) * Box(cover_length - 2*wall_thickness, rib_thickness, rib_height)

snap_tab = Pos(0, cover_width/2 + snap_tab_thickness/2, 0) * Box(snap_tab_width, snap_tab_thickness, snap_tab_height)
snap_tab = fillet(snap_tab.edges(), snap_fillet_radius)
result = result + snap_tab

part = result
part.name = "cover_with_ribs_and_snap_tab"
export_step(part, "output.step")
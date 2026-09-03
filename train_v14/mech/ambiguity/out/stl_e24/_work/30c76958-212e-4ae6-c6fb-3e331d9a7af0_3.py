from build123d import *

cover_length = 80.0
cover_width = 60.0
cover_thickness = 12.0
wall_thickness = 4.0
pocket_depth = 6.0
pocket_margin = 6.0
mount_hole_dia = 4.0
mount_hole_offset = 10.0
rib_height = 2.0
rib_thickness = 2.0
rib_spacing = 15.0
snap_tab_width = 20.0
snap_tab_height = 6.0
snap_tab_thickness = 2.0
chamfer_size = 0.5

result = Box(cover_length, cover_width, cover_thickness)

cavity = Pos(0, 0, -wall_thickness/2) * Box(cover_length - 2*wall_thickness, cover_width - 2*wall_thickness, cover_thickness - wall_thickness)
result = result - cavity

pocket = Pos(0, 0, cover_thickness/2 - pocket_depth/2) * Box(cover_length - 2*pocket_margin, cover_width - 2*pocket_margin, pocket_depth)
result = result - pocket

hole_positions = [
    (-cover_length/2 + mount_hole_offset, -cover_width/2 + mount_hole_offset),
    (cover_length/2 - mount_hole_offset, -cover_width/2 + mount_hole_offset),
    (-cover_length/2 + mount_hole_offset, cover_width/2 - mount_hole_offset),
    (cover_length/2 - mount_hole_offset, cover_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, cover_thickness)

rib_count = int((cover_width - 2*wall_thickness) // rib_spacing) + 1
for i in range(rib_count):
    y_pos = -cover_width/2 + wall_thickness + i * rib_spacing
    rib = Pos(0, y_pos, -rib_height/2) * Box(cover_length - 2*wall_thickness, rib_thickness, rib_height)
    result = result + rib

snap_tab = Pos(0, cover_width/2 + snap_tab_thickness/2, 0) * Box(snap_tab_width, snap_tab_thickness, snap_tab_height)
result = result + snap_tab

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "cover_with_cavity_pocket_ribs"
export_step(part, "output.step")
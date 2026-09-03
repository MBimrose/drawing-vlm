from build123d import *

cover_length = 80.0
cover_width = 60.0
cover_thickness = 12.0
wall_thickness = 4.0
tab_width = 20.0
tab_height = 8.0
tab_thickness = 2.0
rib_height = 3.0
rib_thickness = 2.0
rib_spacing = 15.0
mount_hole_dia = 4.0
mount_hole_offset = 10.0
chamfer_size = 0.5

result = Box(cover_length, cover_width, cover_thickness)

tab = Pos(0, cover_width/2 + tab_thickness/2, 0) * Box(tab_width, tab_thickness, tab_height)
result = result + tab

inner_length = cover_length - 2 * wall_thickness
inner_width = cover_width - 2 * wall_thickness
cavity_depth = cover_thickness - wall_thickness
cavity = Pos(0, 0, -cover_thickness/2 + cavity_depth/2) * Box(inner_length, inner_width, cavity_depth)
result = result - cavity

rib_count = int((inner_width - rib_thickness) // rib_spacing) + 1
for i in range(rib_count):
    y_pos = -inner_width/2 + rib_thickness/2 + i * rib_spacing
    rib = Pos(0, y_pos, -cover_thickness/2 + wall_thickness + rib_height/2) * Box(inner_length, rib_thickness, rib_height)
    result = result + rib

hole_positions = [
    (-cover_length/2 + mount_hole_offset, -cover_width/2 + mount_hole_offset),
    ( cover_length/2 - mount_hole_offset, -cover_width/2 + mount_hole_offset),
    (-cover_length/2 + mount_hole_offset,  cover_width/2 - mount_hole_offset),
    ( cover_length/2 - mount_hole_offset,  cover_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    hole = Pos(x, y, 0) * Cylinder(mount_hole_dia/2, cover_thickness)
    result = result - hole

part = result
part.name = "cover_with_tabs_ribs_and_holes"
export_step(part, "output.step")
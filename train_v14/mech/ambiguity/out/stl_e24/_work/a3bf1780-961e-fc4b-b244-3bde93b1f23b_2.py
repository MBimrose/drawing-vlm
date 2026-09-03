from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
base_thickness = 8.0
rib_thickness = 2.0
rib_height = 10.0
rib_length = 6.0
mount_hole_dia = 2.0
mount_hole_offset = 5.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
cavity_height = outer_height - base_thickness

outer_box = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
cavity = Pos(0, 0, base_thickness + cavity_height / 2) * Box(inner_length, inner_width, cavity_height)
base = outer_box - cavity

rib1 = Pos(-inner_length / 2 + rib_length / 2, 0, base_thickness + rib_height / 2) * Box(rib_length, rib_thickness, rib_height)
rib2 = Pos(inner_length / 2 - rib_length / 2, 0, base_thickness + rib_height / 2) * Box(rib_length, rib_thickness, rib_height)
with_ribs = base + rib1 + rib2

hole_r = mount_hole_dia / 2
hole_h = outer_height + 10
hole_pts = [
    (-outer_length / 2 + mount_hole_offset, -outer_width / 2 + mount_hole_offset),
    ( outer_length / 2 - mount_hole_offset, -outer_width / 2 + mount_hole_offset),
    (-outer_length / 2 + mount_hole_offset,  outer_width / 2 - mount_hole_offset),
    ( outer_length / 2 - mount_hole_offset,  outer_width / 2 - mount_hole_offset),
]
result = with_ribs
for x, y in hole_pts:
    result = result - Pos(x, y, outer_height / 2) * Cylinder(hole_r, hole_h)

part = result
part.name = "box_with_cavity_ribs_and_mount_holes"
export_step(part, "output.step")
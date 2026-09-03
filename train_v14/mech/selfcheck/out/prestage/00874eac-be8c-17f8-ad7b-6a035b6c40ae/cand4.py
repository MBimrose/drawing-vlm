from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
pocket_depth = 5.0
pocket_margin = 5.0
mount_hole_dia = 4.0
mount_hole_offset = 10.0
chamfer_size = 1.0

base = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[bottom_face])

pocket_w = outer_length - 2 * wall_thickness - 2 * pocket_margin
pocket_h = outer_width - 2 * wall_thickness - 2 * pocket_margin
pocket = Pos(0, 0, outer_height - pocket_depth / 2) * Box(pocket_w, pocket_h, pocket_depth)
base = base - pocket

hole_r = mount_hole_dia / 2
hole_h = outer_height + 10
for x, y in [
    (-outer_length / 2 + mount_hole_offset, -outer_width / 2 + mount_hole_offset),
    (outer_length / 2 - mount_hole_offset, -outer_width / 2 + mount_hole_offset),
    (-outer_length / 2 + mount_hole_offset, outer_width / 2 - mount_hole_offset),
    (outer_length / 2 - mount_hole_offset, outer_width / 2 - mount_hole_offset),
]:
    base = base - Pos(x, y, outer_height / 2) * Cylinder(hole_r, hole_h)

vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_size)

part = base
part.name = "hollow_box_with_pocket_and_holes"
export_step(part, "output.step")
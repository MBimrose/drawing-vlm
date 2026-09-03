from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_width = 5.0
rib_height = 10.0
rib_spacing = 12.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 5.0
mount_hole_dia = 4.0
chamfer_size = 0.5

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness

base = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib_count = int((inner_length - rib_spacing) // (rib_width + rib_spacing))
rib_positions = [(-inner_length / 2 + rib_spacing + i * (rib_width + rib_spacing) + rib_width / 2, 0) for i in range(rib_count)]

for x, y in rib_positions:
    base = base - Pos(x, y, rib_height / 2) * Box(rib_width, inner_width, rib_height)

base = base - Pos(0, 0, outer_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)

hole = Pos(outer_length / 2, 0, outer_height / 2) * Rot(0, 90, 0) * Cylinder(mount_hole_dia / 2, outer_length)
base = base - hole

vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_size)

part = base
part.name = "enclosure_with_ribs_pocket"
export_step(part, "output.step")
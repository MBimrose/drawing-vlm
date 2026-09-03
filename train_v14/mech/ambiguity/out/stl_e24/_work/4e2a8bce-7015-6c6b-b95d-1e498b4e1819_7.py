from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
lid_thickness = 2.0
vent_length = 40.0
vent_width = 30.0
vent_depth = 1.5
mount_hole_diameter = 2.0
mount_hole_offset = 5.0
chamfer_size = 0.5

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness

base = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
cavity = Pos(0, 0, wall_thickness + inner_height / 2) * Box(inner_length, inner_width, inner_height)
base = base - cavity

vent = Pos(0, 0, outer_height - vent_depth / 2) * Box(vent_length, vent_width, vent_depth)
base = base - vent

lid = Pos(0, 0, outer_height + lid_thickness / 2) * Box(outer_length, outer_width, lid_thickness)
result = base + lid

hole_positions = [
    (-outer_length / 2 + mount_hole_offset, -outer_width / 2 + mount_hole_offset),
    (outer_length / 2 - mount_hole_offset, -outer_width / 2 + mount_hole_offset),
    (-outer_length / 2 + mount_hole_offset, outer_width / 2 - mount_hole_offset),
    (outer_length / 2 - mount_hole_offset, outer_width / 2 - mount_hole_offset),
]
for x, y in hole_positions:
    hole = Pos(x, y, outer_height + lid_thickness / 2) * Cylinder(mount_hole_diameter / 2, lid_thickness + 1)
    result = result - hole

bottom_face = result.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
result = chamfer(bottom_edges, chamfer_size)

part = result
part.name = "ventilated_box_with_lid"
export_step(part, "output.step")
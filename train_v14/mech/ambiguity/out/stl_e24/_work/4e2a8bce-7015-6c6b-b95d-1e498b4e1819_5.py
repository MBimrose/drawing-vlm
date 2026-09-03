from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
lid_thickness = 3.0
pocket_depth = 5.0
pocket_margin = 5.0
mount_hole_diameter = 2.0
mount_hole_offset = 5.0
chamfer_distance = 0.5

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
pocket_length = inner_length - 2 * pocket_margin
pocket_width = inner_width - 2 * pocket_margin

base = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
cavity = Pos(0, 0, wall_thickness + (outer_height - wall_thickness) / 2) * Box(inner_length, inner_width, outer_height - wall_thickness)
base = base - cavity

pocket = Pos(0, 0, outer_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

hole_r = mount_hole_diameter / 2
hole_h = outer_height + 10
for x in [-outer_length / 2 + mount_hole_offset, outer_length / 2 - mount_hole_offset]:
    for y in [-outer_width / 2 + mount_hole_offset, outer_width / 2 - mount_hole_offset]:
        base = base - Pos(x, y, outer_height / 2) * Cylinder(hole_r, hole_h)

bottom_face = base.faces().sort_by(Axis.Z)[0]
base = chamfer(bottom_face.edges(), chamfer_distance)

part = base
part.name = "box_with_cavity_pocket_holes"
export_step(part, "output.step")
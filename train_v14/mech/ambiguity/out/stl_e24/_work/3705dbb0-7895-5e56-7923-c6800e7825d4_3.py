from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
rib_height = 4.0
rib_thickness = 2.0
hole_diameter = 1.5
hole_spacing = 10.0
mount_hole_diameter = 3.0
mount_hole_offset = 5.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness
rib_outer_length = inner_length + 2 * rib_thickness
rib_outer_width = inner_width + 2 * rib_thickness

base = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, 0, wall_thickness + rib_height / 2) * Box(rib_outer_length, rib_outer_width, rib_height)
result = base + rib

hole_count_x = int((inner_length - 2 * wall_thickness) // hole_spacing) + 1
hole_count_y = int((inner_width - 2 * wall_thickness) // hole_spacing) + 1
for i in range(hole_count_x):
    for j in range(hole_count_y):
        x = (i - (hole_count_x - 1) / 2) * hole_spacing
        y = (j - (hole_count_y - 1) / 2) * hole_spacing
        result = result - Pos(x, y, outer_height / 2) * Cylinder(hole_diameter / 2, outer_height + 1)

result = result - Pos(outer_length / 2, 0, outer_height / 2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, outer_length + 1)
result = result - Pos(-outer_length / 2, 0, outer_height / 2) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, outer_length + 1)

part = result
part.name = "hollow_box_with_rib_and_holes"
export_step(part, "output.step")
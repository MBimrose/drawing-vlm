from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = 4.0
rib_spacing = 10.0
mount_hole_diameter = 3.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 20.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib_length = outer_length - 2 * wall_thickness
rib_count = int((outer_width - 2 * wall_thickness) // (rib_spacing + rib_thickness))
rib_positions = [-(outer_width/2 - wall_thickness - rib_thickness/2) + i * (rib_spacing + rib_thickness) for i in range(rib_count)]

for y in rib_positions:
    rib = Pos(0, y, outer_height - wall_thickness - rib_height/2) * Box(rib_length, rib_thickness, rib_height)
    base = base + rib

hole_r = mount_hole_diameter / 2
for x in [-mount_hole_spacing_x/2, mount_hole_spacing_x/2]:
    for y in [-mount_hole_spacing_y/2, mount_hole_spacing_y/2]:
        hole = Pos(x, y, outer_height/2) * Cylinder(hole_r, outer_height + 10)
        base = base - hole

part = base
part.name = "shelled_box_with_ribs_and_holes"
export_step(part, "output.step")
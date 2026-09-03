from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 3.0
rib_width = 30.0
rib_height = 10.0
front_chamfer = 2.0
mount_hole_diameter = 4.0
mount_hole_spacing_x = 60.0
mount_hole_spacing_y = 30.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(outer_length - 2*wall_thickness, rib_width, rib_height)
base = base + rib

front_face = base.faces().sort_by(Axis.X)[-1]
base = chamfer(front_face.edges(), front_chamfer)

hole_r = mount_hole_diameter / 2
for dx in [-mount_hole_spacing_x/2, mount_hole_spacing_x/2]:
    for dy in [-mount_hole_spacing_y/2, mount_hole_spacing_y/2]:
        base = base - Pos(dx, dy, outer_height/2) * Cylinder(hole_r, outer_height + 10)

part = base
part.name = "hollow_box_with_rib"
export_step(part, "output.step")
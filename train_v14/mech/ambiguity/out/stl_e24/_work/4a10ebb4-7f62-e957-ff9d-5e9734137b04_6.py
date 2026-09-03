from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
lid_thickness = 2.0
base_thickness = 2.0
rib_thickness = 2.0
rib_height = 6.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
cavity_height = outer_height - base_thickness - lid_thickness

body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
cavity = Pos(0, 0, cavity_height/2) * Box(inner_length, inner_width, cavity_height)
body = body - cavity

lid = Pos(0, 0, outer_height + lid_thickness/2) * Box(outer_length, outer_width, lid_thickness)
base = Pos(0, 0, -base_thickness/2) * Box(outer_length, outer_width, base_thickness)
rib = Pos(0, 0, -base_thickness - rib_height/2) * Box(inner_length, rib_thickness, rib_height)

part = body + lid + base + rib

hole_r = mount_hole_diameter / 2
hole_h = 100.0
for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    part = part - Pos(x, 0, outer_height + lid_thickness/2) * Cylinder(hole_r, hole_h)
    part = part - Pos(x, 0, -base_thickness - rib_height/2) * Cylinder(hole_r, hole_h)

part.name = "box_with_lid_base_rib"
export_step(part, "output.step")
from build123d import *

bracket_length = 80.0
bracket_width = 30.0
bracket_thickness = 8.0
fillet_radius = 2.0
pocket_length = 40.0
pocket_width = 12.0
pocket_depth = 4.0
through_hole_diameter = 5.0
through_hole_offset_x = 25.0
mount_hole_diameter = 8.0
mount_hole_spacing = 20.0
mount_hole_offset_x = 10.0
rib_width = 6.0
rib_height = 4.0
rib_thickness = 3.0

base = Pos(0, 0, bracket_thickness/2) * Box(bracket_length, bracket_width, bracket_thickness)
base = fillet(base.edges(), fillet_radius)

rib = Pos(0, 0, -rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
result = base + rib

pocket = Pos(0, 0, bracket_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

through_hole_x = through_hole_offset_x - bracket_length/2
through_hole = Pos(through_hole_x, 0, bracket_thickness/2) * Cylinder(through_hole_diameter/2, bracket_thickness + 1)
result = result - through_hole

mount_hole_x = mount_hole_offset_x - bracket_length/2
for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    mount_hole = Pos(mount_hole_x, y, 0) * Cylinder(mount_hole_diameter/2, bracket_thickness + 1)
    result = result - mount_hole

part = result
part.name = "bracket"
export_step(part, "output.step")
from build123d import *

bracket_length = 80.0
bracket_width = 30.0
bracket_thickness = 8.0
pocket_length = 40.0
pocket_width = 12.0
pocket_depth = 4.0
hole_diameter = 5.0
hole_offset_x = 25.0
hole_offset_y = 0.0
fillet_radius = 2.0
rib_width = 6.0
rib_height = 4.0
rib_thickness = 3.0
mount_hole_diameter = 8.0
mount_hole_spacing = 20.0

solid_body = Box(bracket_length, bracket_width, bracket_thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket = Pos(0, 0, bracket_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole_x = hole_offset_x - bracket_length/2
hole_y = hole_offset_y
solid_body = solid_body - Pos(hole_x, hole_y, 0) * Cylinder(hole_diameter/2, bracket_thickness)

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(0, y, -bracket_thickness/2 + 1.5/2) * Cylinder(mount_hole_diameter/2, 1.5)

rib = Pos(0, 0, -bracket_thickness/2 - rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "bracket"
export_step(part, "output.step")
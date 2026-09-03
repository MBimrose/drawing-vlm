from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 8.0
fillet_radius = 2.0
pocket_length = 40.0
pocket_width = 12.0
pocket_depth = 4.0
hole_diameter = 5.0
hole_offset_x = -leaf_length / 4.0
hole_offset_y = 0.0
rib_height = 3.0
rib_width = 6.0
rib_offset = 10.0
mount_hole_diameter = 8.0
mount_hole_spacing = 20.0
mount_hole_offset_x = -leaf_length / 2.0 + 15.0

solid_body = Box(leaf_length, leaf_width, leaf_thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket = Pos(0, 0, leaf_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

through_hole = Pos(hole_offset_x, hole_offset_y, 0) * Cylinder(hole_diameter/2, leaf_thickness + 1)
solid_body = solid_body - through_hole

rib = Pos(0, 0, -leaf_thickness/2 - rib_height/2) * Box(rib_width, leaf_thickness, rib_height)
solid_body = solid_body + rib

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    mount_hole = Pos(mount_hole_offset_x, y, -leaf_thickness/2 + leaf_thickness/4) * Cylinder(mount_hole_diameter/2, leaf_thickness/2)
    solid_body = solid_body - mount_hole

part = solid_body
part.name = "leaf_with_pocket_and_rib"
export_step(part, "output.step")
from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 8.0
fillet_radius = 2.0
pocket_length = 40.0
pocket_width = 12.0
pocket_depth = 4.0
through_hole_diameter = 5.0
mount_hole_diameter = 5.0
mount_hole_counterbore_diameter = 8.0
mount_hole_counterbore_depth = 3.0
mount_hole_spacing = 25.0
rib_width = 6.0
rib_height = 4.0
rib_thickness = 3.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

through_hole = Cylinder(through_hole_diameter/2, plate_thickness + 1)
solid_body = solid_body - through_hole

for y in [mount_hole_spacing/2, -mount_hole_spacing]:
    cbore = Pos(0, y, -plate_thickness/2) * Cylinder(mount_hole_counterbore_diameter/2, mount_hole_counterbore_depth)
    solid_body = solid_body - cbore

rib = Pos(0, 0, -plate_thickness/2 - rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pocket_and_rib"
export_step(part, "output.step")
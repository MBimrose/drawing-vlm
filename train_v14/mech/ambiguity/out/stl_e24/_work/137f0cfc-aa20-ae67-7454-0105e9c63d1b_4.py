from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
central_hole_diameter = 30.0
mount_hole_diameter = 10.0
mount_hole_spacing = 30.0
tab_width = 20.0
tab_height = 15.0
fillet_radius = 1.0
rib_width = 5.0
rib_length = 40.0
rib_height = 2.0
rib_offset_y = -20.0
pocket_depth = 2.0
pocket_width = 30.0
pocket_length = 20.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_thickness)
for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)
tab = Pos(0, plate_width/2 + tab_height/2, 0) * Box(tab_width, tab_height, plate_thickness)
solid_body = solid_body + tab
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)
rib = Pos(0, rib_offset_y, -plate_thickness/2 - rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib
pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

part = solid_body
part.name = "plate_with_holes_tab_rib_pocket"
export_step(part, "output.step")
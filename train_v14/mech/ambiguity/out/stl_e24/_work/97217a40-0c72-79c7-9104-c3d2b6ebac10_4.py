from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_height = 6.0
rib_width = 10.0
rib_length = plate_length - 10.0
hole_diameter = 12.0
chamfer_size = 1.0
mount_hole_dia = 5.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 20.0
pocket_depth = 2.0
pocket_margin = 5.0

solid_body = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, -plate_thickness/2 + pocket_depth/2) * Box(plate_length - 2*pocket_margin, plate_width - 2*pocket_margin, pocket_depth)
solid_body = solid_body - pocket

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Cylinder(hole_diameter/2, 100)

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, 100)

part = solid_body
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")
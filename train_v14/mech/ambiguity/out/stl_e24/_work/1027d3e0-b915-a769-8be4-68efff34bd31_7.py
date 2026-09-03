from build123d import *

plate_width = 80.0
plate_height = 40.0
plate_thickness = 8.0
chamfer_size = 2.0
central_hole_diameter = 12.0
mount_hole_diameter = 6.0
mount_hole_offset = 10.0
rib_width = 6.0
rib_height = 20.0

base = Box(plate_width, plate_thickness, plate_height)
rib_top = Pos(0, 0, plate_height/2 - rib_height/2) * Box(rib_width, plate_thickness, rib_height)
rib_bottom = Pos(0, 0, -plate_height/2 + rib_height/2) * Box(rib_width, plate_thickness, rib_height)
solid_body = base + rib_top + rib_bottom

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_height + 10)

mount_points = [
    (-plate_width/2 + mount_hole_offset, -plate_height/2 + mount_hole_offset),
    ( plate_width/2 - mount_hole_offset, -plate_height/2 + mount_hole_offset),
    (-plate_width/2 + mount_hole_offset,  plate_height/2 - mount_hole_offset),
    ( plate_width/2 - mount_hole_offset,  plate_height/2 - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_height + 10)

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")
from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 8.0
cutout_diameter = 30.0
hole_diameter = 6.0
hole_spacing = 20.0
rib_thickness = 4.0
rib_height = plate_height * 0.6
rib_offset = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0

solid_body = Box(plate_width, plate_thickness, plate_height)
solid_body = solid_body - Rot(90, 0, 0) * Cylinder(cutout_diameter/2, plate_thickness)

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, plate_thickness)

mount_points = [
    (-plate_width/2 + mount_hole_offset, -plate_height/2 + mount_hole_offset),
    ( plate_width/2 - mount_hole_offset, -plate_height/2 + mount_hole_offset),
    (-plate_width/2 + mount_hole_offset,  plate_height/2 - mount_hole_offset),
    ( plate_width/2 - mount_hole_offset,  plate_height/2 - mount_hole_offset)
]
for x, z in mount_points:
    solid_body = solid_body - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

rib = Box(rib_thickness, rib_thickness, rib_height)
solid_body = solid_body + Pos(-plate_width/2 - rib_thickness/2, -plate_thickness/2 - rib_offset, 0) * rib
solid_body = solid_body + Pos(plate_width/2 + rib_thickness/2, -plate_thickness/2 - rib_offset, 0) * rib

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")
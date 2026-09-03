from build123d import *

plate_width = 80.0
plate_height = 50.0
plate_thickness = 8.0
cutout_diameter = 30.0
mount_hole_diameter = 5.0
mount_hole_offset = 12.0
clearance_hole_diameter = 6.0
clearance_hole_spacing = 20.0
rib_thickness = 4.0
rib_height = 30.0
rib_offset = 2.0

solid_body = Box(plate_width, plate_thickness, plate_height)
solid_body = solid_body - Rot(90, 0, 0) * Cylinder(cutout_diameter/2, plate_thickness + 20)

mount_points = [
    (-plate_width/2 + mount_hole_offset, -plate_height/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, -plate_height/2 + mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, plate_height/2 - mount_hole_offset),
    (plate_width/2 - mount_hole_offset, plate_height/2 - mount_hole_offset),
]
for x, z in mount_points:
    solid_body = solid_body - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 20)

clearance_points = [
    (-clearance_hole_spacing/2, 0),
    (clearance_hole_spacing/2, 0),
]
for x, z in clearance_points:
    solid_body = solid_body - Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(clearance_hole_diameter/2, plate_thickness + 20)

rib = Box(rib_thickness, rib_thickness, rib_height)
solid_body = solid_body + Pos(plate_width/2 + rib_offset, -plate_thickness/2 - rib_thickness/2, 0) * rib
solid_body = solid_body + Pos(-plate_width/2 - rib_offset, -plate_thickness/2 - rib_thickness/2, 0) * rib

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")
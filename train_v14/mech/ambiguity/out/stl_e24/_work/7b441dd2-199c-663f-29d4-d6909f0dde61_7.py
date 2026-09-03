from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 10.0
central_hole_diameter = 25.4
mount_hole_diameter = 6.3
mount_hole_offset_x = 20.0
mount_hole_offset_y = 10.0
rib_width = 8.0
rib_height = 4.0
rib_spacing = 30.0
countersink_angle = 82.0
chamfer_distance = 1.0

solid_body = Box(plate_length, plate_width, plate_thickness)

solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_thickness)

mount_points = [
    (-plate_length/2 + mount_hole_offset_x, -plate_width/2 + mount_hole_offset_y),
    ( plate_length/2 - mount_hole_offset_x, -plate_width/2 + mount_hole_offset_y),
    (-plate_length/2 + mount_hole_offset_x,  plate_width/2 - mount_hole_offset_y),
    ( plate_length/2 - mount_hole_offset_x,  plate_width/2 - mount_hole_offset_y)
]

for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * CounterSinkHole(mount_hole_diameter/2, plate_thickness/2, plate_thickness, countersink_angle)

rib1 = Pos(-plate_length/2 + rib_spacing/2, 0, rib_height/2) * Box(rib_width, rib_height, rib_height)
rib2 = Pos(plate_length/2 - rib_spacing/2, 0, rib_height/2) * Box(rib_width, rib_height, rib_height)
solid_body = solid_body + rib1 + rib2

solid_body = chamfer(solid_body.edges(), chamfer_distance)

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")
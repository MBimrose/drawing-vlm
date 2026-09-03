from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 12.0
bearing_diameter = 30.0
bearing_depth = 6.0
mount_hole_diameter = 5.0
mount_hole_offset = 15.0
countersink_diameter = 10.0
countersink_angle = 82.0
rib_thickness = 4.0
rib_height = 6.0
chamfer_size = 1.0

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Pos(0, plate_width/2 - rib_thickness/2, 0) * Box(rib_height, rib_thickness, plate_thickness)
rib2 = Pos(0, -plate_width/2 + rib_thickness/2, 0) * Box(rib_height, rib_thickness, plate_thickness)
solid_body = base + rib1 + rib2

solid_body = solid_body - Pos(0, 0, plate_thickness/2 - bearing_depth/2) * Cylinder(bearing_diameter/2, bearing_depth)

hole_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * CounterSinkHole(mount_hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")
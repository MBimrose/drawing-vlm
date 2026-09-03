from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 12.0
pocket_diameter = 30.0
pocket_depth = 6.0
fillet_radius = 3.0
chamfer_distance = 0.8
mount_hole_diameter = 4.0
mount_hole_offset = 15.0
rib_width = 10.0
rib_height = 4.0
rib_offset_y = 20.0
counterbore_diameter = 6.0
counterbore_depth = 4.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = solid_body - Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(0, rib_offset_y, -plate_thickness/2 + rib_height/2) * Box(rib_width, rib_height, rib_height)
solid_body = solid_body + rib

hole_positions = [
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

part = solid_body
part.name = "plate_with_pocket_rib_and_holes"
export_step(part, "output.step")
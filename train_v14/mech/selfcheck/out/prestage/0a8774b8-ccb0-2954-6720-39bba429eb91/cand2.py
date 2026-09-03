from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
edge_chamfer = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
vent_hole_diameter = 4.0
vent_rows = 2
vent_cols = 3
vent_spacing_x = 12.0
vent_spacing_y = 12.0
vent_offset_x = 10.0
vent_offset_y = 10.0
rib_thickness = 4.0
rib_height = 20.0
rib_offset = 5.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), edge_chamfer)

mount_points = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness * 2)

vent_points = []
for i in range(vent_cols):
    for j in range(vent_rows):
        x = vent_offset_x + i * vent_spacing_x
        y = vent_offset_y + j * vent_spacing_y
        vent_points.append((x, y))
for x, y in vent_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(vent_hole_diameter/2, plate_thickness * 2)

rib = Pos(-plate_length/2 + rib_offset, 0, 0) * Box(rib_thickness, rib_height, plate_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")
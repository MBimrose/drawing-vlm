from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_height = 2.0
rib_width = 4.0
rib_spacing = 10.0
rib_margin = 5.0
chamfer_size = 0.8
mount_hole_dia = 4.0
mount_hole_offset = 15.0
vent_hole_dia = 3.0
vent_rows = 2
vent_cols = 4
vent_spacing_x = 10.0
vent_spacing_y = 12.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib_count = int((plate_length - 2 * rib_margin) // rib_spacing) + 1
for i in range(rib_count):
    x = -plate_length/2 + rib_margin + i * rib_spacing
    rib = Pos(x, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width - 2 * rib_margin, rib_height)
    solid_body = solid_body + rib

for y in [-plate_width/2 + mount_hole_offset, plate_width/2 - mount_hole_offset]:
    hole = Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, plate_length)
    solid_body = solid_body - hole

for i in range(vent_cols):
    for j in range(vent_rows):
        x = (i - (vent_cols-1)/2) * vent_spacing_x
        y = (j - (vent_rows-1)/2) * vent_spacing_y
        hole = Pos(x, y, 0) * Cylinder(vent_hole_dia/2, plate_thickness)
        solid_body = solid_body - hole

part = solid_body
part.name = "ribbed_plate_with_holes"
export_step(part, "output.step")
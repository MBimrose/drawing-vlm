from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
rib_width = 8.0
rib_height = 4.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 2
hole_cols = 3
hole_offset_x = 20.0
hole_offset_y = 10.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_distance = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width, rib_height)
solid_body = solid_body + rib

pocket = Pos(0, 0, plate_thickness/2 + rib_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = hole_offset_x + (i - (hole_cols-1)/2) * hole_spacing_x
        y = hole_offset_y + (j - (hole_rows-1)/2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, 20)

corner_positions = [
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
]
for x, y in corner_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, 20)

part = solid_body
part.name = "plate_with_rib_pockets_and_holes"
export_step(part, "output.step")
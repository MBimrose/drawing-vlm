from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 5.0
chamfer_size = 1.0
pocket_width = 40.0
pocket_depth = 30.0
pocket_depth_cut = 3.0
hole_diameter = 3.0
hole_spacing = 8.0
hole_rows = 4
hole_cols = 6
mount_hole_diameter = 5.0
mount_hole_offset = 8.0
rib_width = 40.0
rib_depth = 30.0
rib_height = 2.0

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing
        y = (j - (hole_rows-1)/2) * hole_spacing
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

corner_x = plate_width / 2 - mount_hole_offset
corner_y = plate_depth / 2 - mount_hole_offset
for sx in [-1, 1]:
    for sy in [-1, 1]:
        solid_body = solid_body - Pos(sx*corner_x, sy*corner_y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

rib = Pos(0, 0, rib_height/2) * Box(rib_width, rib_depth, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pocket_holes_and_rib"
export_step(part, "output.step")
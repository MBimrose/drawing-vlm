from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 5.0
edge_chamfer = 0.8
hole_diameter = 3.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = 10.0
hole_spacing_y = 12.0
mount_hole_diameter = 4.0
mount_hole_offset = 15.0
rib_height = 2.0
rib_thickness = 2.0
rib_spacing = 8.0
rib_margin = 5.0

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), edge_chamfer)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness + 1)

for y in [-plate_depth / 2 + mount_hole_offset, plate_depth / 2 - mount_hole_offset]:
    solid_body = solid_body - Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, plate_width + 1)

num_ribs = int((plate_width - 2 * rib_margin) // rib_spacing) + 1
for i in range(num_ribs):
    x = -plate_width / 2 + rib_margin + i * rib_spacing
    rib = Pos(x, 0, -plate_thickness / 2 + rib_height / 2) * Box(rib_thickness, plate_depth - 2 * rib_margin, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")
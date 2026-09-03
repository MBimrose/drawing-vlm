from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
rib_width = 8.0
rib_height = 4.0
rib_offset = 5.0
recess_diameter = 30.0
recess_depth = 2.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 30.0
hole_rows = 2
hole_cols = 4
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Pos(-plate_length/2 + rib_offset + rib_width/2, 0, 0) * Box(rib_width, rib_height, plate_thickness)
rib2 = Pos(plate_length/2 - rib_offset - rib_width/2, 0, 0) * Box(rib_width, rib_height, plate_thickness)
solid_body = base + rib1 + rib2

solid_body = solid_body - Pos(0, 0, plate_thickness/2 - recess_depth/2) * Cylinder(recess_diameter/2, recess_depth)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_ribs_recess_and_holes"
export_step(part, "output.step")
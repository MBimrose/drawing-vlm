from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
cutout_width = 40.0
cutout_depth = 30.0
hole_diameter = 4.0
hole_depth = 6.0
hole_spacing_x = 20.0
hole_spacing_y = 30.0
hole_rows = 2
hole_cols = 3
chamfer_size = 1.0
fillet_radius = 2.0
rib_width = 10.0
rib_height = 5.0
rib_thickness = 2.0

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = chamfer(solid_body.edges().filter_by(Axis.X), chamfer_size)

cutout = Box(cutout_width, cutout_depth, plate_thickness)
solid_body = solid_body - cutout

rib = Pos(0, 0, plate_thickness/2 - rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, plate_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
        solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_cutout_rib_holes"
export_step(part, "output.step")
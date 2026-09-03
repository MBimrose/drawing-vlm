from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 5.0
rib_height = 2.0
pocket_diameter = 30.0
pocket_depth = 2.0
hole_diameter = 5.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = 20.0
hole_spacing_y = 30.0
chamfer_size = 0.5

base = Box(plate_width, plate_depth, plate_thickness)
rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_width, plate_depth, rib_height)
solid_body = base + rib

pocket = Pos(0, 0, plate_thickness/2 + rib_height - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)
solid_body = solid_body - pocket

hole_r = hole_diameter / 2
hole_h = plate_thickness + rib_height + 10
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_rib_pocket_holes"
export_step(part, "output.step")
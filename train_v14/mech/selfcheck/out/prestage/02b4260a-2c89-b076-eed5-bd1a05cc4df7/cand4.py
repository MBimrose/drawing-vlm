from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_height = 2.0
rib_width = 5.0
pocket_diameter = 30.0
pocket_depth = 3.0
hole_diameter = 5.0
hole_rows = 2
hole_cols = 4
hole_spacing_x = 20.0
hole_spacing_y = 30.0
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Pos(0, plate_width/2 - rib_width/2, 0) * Box(plate_length, rib_width, rib_height)
rib2 = Pos(0, -(plate_width/2 - rib_width/2), 0) * Box(plate_length, rib_width, rib_height)
solid_body = base + rib1 + rib2

solid_body = solid_body - Pos(0, 0, plate_thickness - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_ribs_pocket_and_holes"
export_step(part, "output.step")
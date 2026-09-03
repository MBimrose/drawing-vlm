from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 6.0
pocket_length = 60.0
pocket_width = 40.0
pocket_depth = 4.0
rib_thickness = 4.0
rib_height = 20.0
hole_diameter = 5.0
hole_depth = 3.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
chamfer_size = 0.8

solid_body = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

rib1 = Pos(-plate_length/2 + rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, plate_thickness)
rib2 = Pos(plate_length/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, plate_thickness)
solid_body = solid_body + rib1 + rib2

for i in range(3):
    for j in range(2):
        x = (i - 1) * hole_spacing_x
        y = (j - 0.5) * hole_spacing_y
        hole = Pos(x, y, plate_thickness/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
        solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_pocket_ribs_and_holes"
export_step(part, "output.step")
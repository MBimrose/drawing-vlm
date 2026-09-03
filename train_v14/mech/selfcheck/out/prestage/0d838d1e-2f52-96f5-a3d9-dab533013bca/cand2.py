from build123d import *

plate_length = 100
plate_width = 60
plate_thickness = 8
pocket_width = 30
pocket_length = 20
pocket_depth = 2
hole_diameter = 6
hole_spacing_x = 20
hole_spacing_y = 20
hole_rows = 2
hole_cols = 4
rib_width = 8
rib_height = 4
rib_spacing = 30
chamfer_size = 0.2

solid = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
solid = solid - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

rib1 = Pos(0, 0, -plate_thickness/2 - rib_height/2) * Box(pocket_width, rib_width, rib_height)
solid = solid + rib1

rib2 = Pos(-rib_spacing, 0, -plate_thickness/2 - rib_height/2) * Box(rib_width, rib_height, rib_height)
solid = solid + rib2

rib3 = Pos(rib_spacing, 0, -plate_thickness/2 - rib_height/2) * Box(rib_width, rib_height, rib_height)
solid = solid + rib3

part = solid
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")
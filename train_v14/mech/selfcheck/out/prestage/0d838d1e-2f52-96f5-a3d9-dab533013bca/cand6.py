from build123d import *

plate_length = 100
plate_width = 60
plate_thickness = 8
pocket_length = 30
pocket_width = 20
pocket_depth = 4
fillet_radius = 0.5
hole_diameter = 6
hole_spacing_x = 20
hole_spacing_y = 20
hole_rows = 2
hole_cols = 4
rib_height = 4
rib_width = 10
rib_spacing = 20

solid_body = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
pocket = fillet(pocket.edges().filter_by(Axis.Z), fillet_radius)
solid_body = solid_body - pocket

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

rib_positions = [
    (-plate_length/2 + rib_spacing, 0),
    (0, 0),
    (plate_length/2 - rib_spacing, 0)
]
for x, y in rib_positions:
    rib = Pos(x, y, -plate_thickness/2 - rib_height/2) * Box(rib_width, rib_height, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")
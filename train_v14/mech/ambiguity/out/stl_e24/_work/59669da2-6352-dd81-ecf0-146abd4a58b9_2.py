from build123d import *

plate_width = 80.0
plate_depth = 30.0
plate_thickness = 5.0
rib_width = 20.0
rib_height = 8.0
rib_offset = 30.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 10.0
hole_rows = 2
hole_cols = 3
fillet_radius = 2.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_depth, plate_thickness)
rib = Pos(rib_offset, 0, plate_thickness + rib_height/2) * Box(rib_width, plate_depth, rib_height)
solid = base + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

solid = fillet(solid.edges(), fillet_radius)
part = solid
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")
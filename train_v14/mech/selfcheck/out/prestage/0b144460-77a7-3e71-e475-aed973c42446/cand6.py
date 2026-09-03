from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
corner_fillet = 2.0
rib_width = 5.0
rib_height = 5.0
rib_spacing = 15.0
rib_count = 4
hole_diameter = 6.0
hole_spacing_x = 12.0
hole_spacing_y = 12.0
hole_rows = 4
hole_cols = 5

base = Box(plate_length, plate_width, plate_thickness)
base = fillet(base.edges(), corner_fillet)

rib_y = plate_width - 2 * corner_fillet - rib_width
for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    rib = Pos(x, 0, plate_thickness / 2 + rib_height / 2) * Box(rib_width, rib_y, rib_height)
    base = base + rib

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness + rib_height + 10)
        base = base - hole

part = base
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")
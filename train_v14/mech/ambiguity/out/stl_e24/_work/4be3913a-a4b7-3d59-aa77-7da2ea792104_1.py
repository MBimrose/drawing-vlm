from build123d import *

plate_width = 60.0
plate_depth = 30.0
plate_thickness = 8.0
pin_radius = 5.0
pin_length = 30.0
hole_diameter = 4.0
hole_spacing = 12.0
hole_rows = 3
hole_cols = 4
fillet_radius = 1.5

base = Box(plate_width, plate_depth, plate_thickness)
pin = Pos(0, 0, plate_thickness/2 + pin_length/2) * Cylinder(pin_radius, pin_length)
solid_body = base + pin

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing
        y = (j - (hole_rows - 1) / 2) * hole_spacing
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

part = solid_body
part.name = "plate_with_pin_and_holes"
export_step(part, "output.step")
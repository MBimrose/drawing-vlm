from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
bearing_diameter = 30.0
bearing_depth = 6.0
hole_diameter = 8.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
fillet_radius = 3.0

solid_body = Box(plate_length, plate_width, plate_thickness)

# Bearing recess on top face
solid_body = solid_body - Pos(0, 0, plate_thickness - bearing_depth/2) * Cylinder(bearing_diameter/2, bearing_depth)

# 2x2 hole pattern through the plate
for i in range(2):
    for j in range(2):
        x = (i - 0.5) * hole_spacing_x
        y = (j - 0.5) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

# Fillet all vertical edges
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "plate_with_bearing_and_holes"
export_step(part, "output.step")
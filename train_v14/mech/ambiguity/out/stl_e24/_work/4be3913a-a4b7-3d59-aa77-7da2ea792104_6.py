from build123d import *

base_length = 70.0
base_width = 30.0
base_thickness = 8.0
pin_radius = 5.0
pin_height = 30.0
hole_diameter = 4.0
hole_spacing_x = 12.0
hole_spacing_y = 8.0
hole_rows = 3
hole_cols = 3
fillet_radius = 1.5

base = Box(base_length, base_width, base_thickness)
pin = Pos(0, 0, base_thickness/2 + pin_height/2) * Cylinder(pin_radius, pin_height)
solid_body = base + pin

hole_points = []
start_x = -((hole_cols - 1) * hole_spacing_x) / 2.0
start_y = -((hole_rows - 1) * hole_spacing_y) / 2.0
for i in range(hole_cols):
    for j in range(hole_rows):
        x = start_x + i * hole_spacing_x
        y = start_y + j * hole_spacing_y
        if (x**2 + y**2) < (pin_radius + hole_diameter) ** 2:
            continue
        hole_points.append((x, y))

for x, y in hole_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "base_with_pin_and_holes"
export_step(part, "output.step")
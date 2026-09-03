from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 4.0
rib_height = 2.0
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 15.0
num_holes_x = 4
num_holes_y = 3
central_hole_diameter = 8.0
fillet_radius = 0.8

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Pos(0, 0, plate_thickness) * Box(plate_length - 2 * rib_width, rib_width, rib_height)
rib2 = Pos(0, 0, plate_thickness) * Box(rib_width, plate_width - 2 * rib_width, rib_height)
result = base + rib1 + rib2

total_height = plate_thickness + rib_height
for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = (i - (num_holes_x - 1) / 2) * hole_spacing_x
        y = (j - (num_holes_y - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, total_height + 1)

result = result - Cylinder(central_hole_diameter / 2, total_height + 1)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

part = result
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")
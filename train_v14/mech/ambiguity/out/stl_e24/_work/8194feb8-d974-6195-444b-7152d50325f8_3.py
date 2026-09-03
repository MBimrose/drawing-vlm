from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 4.0
hole_diameter = 5.0
hole_spacing = 12.0
num_holes = 8
chamfer_distance = 1.0
rib_width = 20.0
rib_height = 2.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

rib = Pos(0, 0, plate_thickness) * Box(rib_width, plate_width - 2 * chamfer_distance, rib_height)
result = base + rib

for i in range(num_holes):
    x = (i - (num_holes - 1) / 2) * hole_spacing
    result = result - Pos(x, 0, plate_thickness + rib_height) * Cylinder(hole_diameter / 2, plate_thickness + rib_height + 10)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")
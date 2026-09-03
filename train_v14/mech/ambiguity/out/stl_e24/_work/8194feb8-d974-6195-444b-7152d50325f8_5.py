from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 4.0
rib_length = 20.0
rib_width = 20.0
rib_height = 2.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_count = 6
chamfer_distance = 1.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

rib = Pos(0, 0, plate_thickness) * Box(rib_length, rib_width, rib_height)
result = base + rib

total_height = plate_thickness + rib_height
for i in range(hole_count):
    x = -((hole_count - 1) * hole_spacing) / 2 + i * hole_spacing
    result = result - Pos(x, 0, total_height / 2) * Cylinder(hole_diameter / 2, total_height + 2)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")
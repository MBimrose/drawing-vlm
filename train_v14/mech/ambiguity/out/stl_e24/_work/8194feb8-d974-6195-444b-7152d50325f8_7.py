from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 4.0
rib_width = 20.0
rib_height = 2.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_edge_offset = 10.0
chamfer_distance = 1.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

rib = Pos(0, 0, plate_thickness) * Box(rib_width, rib_width, rib_height)
rib = chamfer(rib.edges().filter_by(Axis.Z), chamfer_distance)

result = base + rib

num_holes = int((plate_length - 2 * hole_edge_offset) // hole_spacing) + 1
for i in range(num_holes):
    x = -plate_length / 2 + hole_edge_offset + i * hole_spacing
    result = result - Pos(x, 0, plate_thickness + rib_height) * Cylinder(hole_diameter / 2, plate_thickness + rib_height + 10)

part = result
part.name = "plate_with_rib_and_holes"
export_step(part, "output.step")
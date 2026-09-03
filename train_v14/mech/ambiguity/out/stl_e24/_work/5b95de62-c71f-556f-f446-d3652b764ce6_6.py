from build123d import *

plate_length = 80.0
plate_width = 80.0
plate_thickness = 10.0
pocket_length = 40.0
pocket_width = 40.0
pocket_depth = 6.0
rib_width = 5.0
rib_height = 3.0
hole_diameter = 5.0
hole_offset = 25.0
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)
rib = Box(plate_length, plate_width, rib_height) - Box(plate_length - 2 * rib_width, plate_width - 2 * rib_width, rib_height)
result = base + rib

pocket = Pos(0, 0, plate_thickness / 2 - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

hole_positions = [
    (hole_offset, hole_offset),
    (hole_offset, -hole_offset),
    (-hole_offset, hole_offset),
    (-hole_offset, -hole_offset),
    (0, hole_offset),
    (0, -hole_offset),
    (hole_offset, 0),
    (-hole_offset, 0),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness + 1)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_pocket_rib_and_holes"
export_step(part, "output.step")
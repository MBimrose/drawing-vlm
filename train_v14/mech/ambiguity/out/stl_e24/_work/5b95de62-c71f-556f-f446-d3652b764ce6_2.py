from build123d import *

plate_size = 80.0
plate_thickness = 10.0
pocket_size = 40.0
hole_diameter = 5.0
hole_spacing = 25.0
chamfer_distance = 0.5

base = Box(plate_size, plate_size, plate_thickness)
pocket = Box(pocket_size, pocket_size, plate_thickness)
solid_body = base - pocket

hole_positions = [
    (-hole_spacing, 0), (0, 0), (hole_spacing, 0),
    (0, -hole_spacing), (0, hole_spacing)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "plate_with_pocket_and_holes"
export_step(part, "output.step")
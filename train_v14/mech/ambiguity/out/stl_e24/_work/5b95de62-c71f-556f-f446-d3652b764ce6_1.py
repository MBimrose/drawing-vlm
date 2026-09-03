from build123d import *

plate_width = 80.0
plate_length = 80.0
plate_thickness = 10.0
pocket_width = 40.0
pocket_length = 40.0
hole_diameter = 5.0
hole_spacing = 25.0
chamfer_size = 0.5

base = Box(plate_width, plate_length, plate_thickness)
pocket = Box(pocket_width, pocket_length, plate_thickness)
solid_body = base - pocket

hole_positions = [
    (hole_spacing, 0), (-hole_spacing, 0),
    (0, hole_spacing), (0, -hole_spacing),
    (hole_spacing, hole_spacing), (-hole_spacing, hole_spacing),
    (hole_spacing, -hole_spacing), (-hole_spacing, -hole_spacing)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_pocket_and_holes"
export_step(part, "output.step")
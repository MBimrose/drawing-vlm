from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 5.0
pocket_depth = 2.0
pocket_margin = 3.0
hole_diameter = 5.0
hole_offset = 10.0
rib_height = 2.0
rib_thickness = 2.0
rib_spacing = 20.0
fillet_radius = 0.5

result = Box(plate_length, plate_width, plate_thickness)

pocket = Box(plate_length - 2 * pocket_margin, plate_width - 2 * pocket_margin, pocket_depth)
result = result - pocket

hole_positions = [
    (-plate_length / 2 + hole_offset, -plate_width / 2 + hole_offset),
    (plate_length / 2 - hole_offset, -plate_width / 2 + hole_offset),
    (-plate_length / 2 + hole_offset, plate_width / 2 - hole_offset),
    (plate_length / 2 - hole_offset, plate_width / 2 - hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness)

rib_count = int((plate_length - 2 * pocket_margin) // rib_spacing) + 1
for i in range(rib_count):
    x = -plate_length / 2 + pocket_margin + i * rib_spacing
    rib = Pos(x, 0, 0) * Box(rib_thickness, plate_width - 2 * pocket_margin, rib_height)
    result = result + rib

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = fillet(bottom_face.edges(), fillet_radius)

part = result
part.name = "plate_with_pocket_holes_and_ribs"
export_step(part, "output.step")
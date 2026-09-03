from build123d import *

plate_length = 100.0
plate_width = 50.0
plate_thickness = 10.0
pocket_depth = 2.0
pocket_margin = 10.0
hole_diameter = 3.0
hole_offset = 10.0
rib_height = 4.0
rib_width = 5.0
rib_spacing = 20.0
chamfer_size = 0.5

solid_body = Box(plate_length, plate_width, plate_thickness)

pocket = Box(plate_length - 2 * pocket_margin, plate_width - 2 * pocket_margin, pocket_depth)
solid_body = solid_body - Pos(0, 0, -pocket_depth / 2) * pocket

hole_positions = [
    (-plate_length / 2 + hole_offset, -plate_width / 2 + hole_offset),
    (plate_length / 2 - hole_offset, -plate_width / 2 + hole_offset),
    (-plate_length / 2 + hole_offset, plate_width / 2 - hole_offset),
    (plate_length / 2 - hole_offset, plate_width / 2 - hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness)

rib_count = int((plate_length - 2 * pocket_margin) // rib_spacing) + 1
rib_positions = [(-plate_length / 2 + pocket_margin + i * rib_spacing, 0) for i in range(rib_count)]
for x, y in rib_positions:
    solid_body = solid_body + Pos(x, y, -plate_thickness / 2 - rib_height / 2) * Box(rib_width, rib_height, rib_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "plate_with_pocket_holes_ribs"
export_step(part, "output.step")
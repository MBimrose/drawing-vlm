from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 5.0
wall_thickness = 3.0
rib_height = 2.0
rib_width = 2.0
rib_spacing = 20.0
hole_diameter = 5.0
hole_offset = 10.0
chamfer_size = 0.5

solid_body = Box(plate_length, plate_width, plate_thickness)

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 1)

rib_count = int((plate_length - 2*wall_thickness) // rib_spacing)
for i in range(rib_count):
    x_pos = -plate_length/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, 0, 0) * Box(rib_width, plate_width, rib_height)
    solid_body = solid_body + rib

pocket = Pos(0, 0, -plate_thickness/2 + 1.0) * Box(plate_length - 2*wall_thickness, plate_width - 2*wall_thickness, 2.0)
solid_body = solid_body - pocket

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "ribbed_plate_with_pocket"
export_step(part, "output.step")
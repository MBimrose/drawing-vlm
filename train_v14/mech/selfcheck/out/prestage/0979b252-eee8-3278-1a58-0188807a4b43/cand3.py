from build123d import *

length = 80.0
width = 30.0
thickness = 8.0
rib_height = 4.0
rib_width = 12.0
rib_offset = 10.0
hex_flat_distance = 6.0
hex_depth = 2.0
hole_diameter = 5.0
hole_spacing = 40.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(length, width)
    extrude(amount=thickness)

solid_body = p.part

rib1 = Pos(-length/2 + rib_offset + rib_width/2, 0, thickness/2) * Box(rib_width, rib_height, thickness)
rib2 = Pos(length/2 - rib_offset - rib_width/2, 0, thickness/2) * Box(rib_width, rib_height, thickness)
solid_body = solid_body + rib1 + rib2

with BuildPart() as hp:
    with BuildSketch() as hs:
        RegularPolygon(hex_flat_distance, 6)
    extrude(amount=hex_depth)
hex_prism = Pos(0, 0, thickness - hex_depth) * hp.part
solid_body = solid_body - hex_prism

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    solid_body = solid_body - Pos(x, y, thickness/2) * Cylinder(hole_diameter/2, thickness)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "ribbed_plate_with_hex_socket"
export_step(part, "output.step")
from build123d import *

length = 80.0
width = 30.0
thickness = 8.0
rib_height = 2.0
rib_width = 6.0
rib_offset = 5.0
hex_flat_distance = 10.0
hex_depth = 6.0
hole_diameter = 5.0
hole_spacing = 40.0
chamfer_size = 0.5

base = Box(length, width, thickness)
rib = Pos(0, width/2 - rib_offset - rib_width/2, thickness/2 - rib_height/2) * Box(rib_width, rib_height, rib_height)
solid_body = base + rib

with BuildPart() as hp:
    with BuildSketch() as hs:
        RegularPolygon(hex_flat_distance/2, 6)
    extrude(amount=hex_depth)
hex_prism = Pos(0, 0, thickness - hex_depth) * hp.part
solid_body = solid_body - hex_prism

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, thickness * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "ribbed_plate_with_hex_socket"
export_step(part, "output.step")
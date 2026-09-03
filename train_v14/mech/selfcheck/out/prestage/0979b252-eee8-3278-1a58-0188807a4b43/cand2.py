from build123d import *

length = 80.0
width = 30.0
thickness = 8.0
rib_height = 2.0
rib_width = 6.0
rib_offset = 5.0
socket_diameter = 10.0
socket_depth = 6.0
chamfer_size = 0.5
hole_diameter = 5.0
hole_spacing = 40.0

base = Pos(0, 0, thickness/2) * Box(length, width, thickness)
rib = Pos(-length/2 + rib_offset + rib_width/2, 0, thickness/2 + rib_height/2) * Box(rib_width, width - 2*rib_offset, rib_height)
result = base + rib

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, thickness/2) * Cylinder(hole_diameter/2, thickness + 1)

with BuildPart() as hp:
    with BuildSketch() as hs:
        RegularPolygon(socket_diameter/2, 6)
    extrude(amount=socket_depth)
hex_prism = hp.part
result = result - Pos(0, 0, thickness) * hex_prism

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_rib_and_socket"
export_step(part, "output.step")
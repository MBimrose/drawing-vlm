from build123d import *

jaw_length = 80.0
jaw_width = 30.0
jaw_thickness = 8.0
rib_height = 4.0
rib_width = 6.0
rib_spacing = 12.0
rib_protrusion = 2.0
hole_diameter = 5.0
hole_spacing = 40.0
hex_socket_diameter = 10.0
hex_socket_depth = 6.0
chamfer_size = 0.5

base = Pos(0, 0, jaw_thickness/2) * Box(jaw_length, jaw_width, jaw_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

rib_count = int((jaw_length - rib_spacing) // rib_spacing)
rib_positions = [(-jaw_length/2 + rib_spacing/2 + i * rib_spacing) for i in range(rib_count)]

for x in rib_positions:
    rib = Pos(x, 0, rib_protrusion/2) * Box(rib_width, rib_height, rib_protrusion)
    base = base + rib

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, 0, jaw_thickness/2) * Cylinder(hole_diameter/2, jaw_thickness + 2)
    base = base - hole

with BuildPart() as hp:
    with BuildSketch() as hs:
        RegularPolygon(hex_socket_diameter/2, 6)
    extrude(amount=hex_socket_depth)
hex_socket = Pos(0, 0, jaw_thickness - hex_socket_depth/2) * hp.part
base = base - hex_socket

part = base
part.name = "jaw_with_ribs_and_socket"
export_step(part, "output.step")
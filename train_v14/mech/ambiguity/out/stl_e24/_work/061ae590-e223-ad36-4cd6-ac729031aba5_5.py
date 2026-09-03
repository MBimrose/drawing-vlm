from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
central_hole_diameter = 12.0
rib_width = 6.0
rib_thickness = 3.0
rib_height = 12.0
rib_spacing_x = 40.0
rib_spacing_y = 40.0
socket_diameter = 16.0
socket_depth = 20.0
socket_offset_x = 30.0
socket_offset_y = 20.0
chamfer_size = 1.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_depth)
        Circle(central_hole_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib_positions = [
    (-rib_spacing_x / 2, -rib_spacing_y / 2),
    (rib_spacing_x / 2, -rib_spacing_y / 2),
    (-rib_spacing_x / 2, rib_spacing_y / 2),
    (rib_spacing_x / 2, rib_spacing_y / 2),
]
for x, y in rib_positions:
    solid_body = solid_body + Pos(x, y, plate_thickness + rib_height / 2) * Box(rib_width, rib_thickness, rib_height)

socket_positions = [
    (-socket_offset_x, -socket_offset_y),
    (socket_offset_x, socket_offset_y),
]
for x, y in socket_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness - socket_depth / 2) * Cylinder(socket_diameter / 2, socket_depth)

part = solid_body
part.name = "plate_with_ribs_and_sockets"
export_step(part, "output.step")
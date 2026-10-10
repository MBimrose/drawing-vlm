from build123d import *

base_length = 80.0
base_width = 80.0
base_thickness = 5.0
hex_radius = 30.0
hex_height = 20.0
draft_angle = 2.0
chamfer_distance = 2.0
mount_hole_dia = 5.0
mount_hole_offset = 10.0
central_hole_radius = 12.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(base_length, base_width)
    extrude(amount=base_thickness)

solid_body = p.part

hole_positions = [
    (base_length/2 - mount_hole_offset, base_width/2 - mount_hole_offset),
    (-base_length/2 + mount_hole_offset, base_width/2 - mount_hole_offset),
    (-base_length/2 + mount_hole_offset, -base_width/2 + mount_hole_offset),
    (base_length/2 - mount_hole_offset, -base_width/2 + mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, base_thickness/2) * Cylinder(mount_hole_dia/2, base_thickness + 1)

with BuildPart() as hex_p:
    with BuildSketch(Plane.XY.offset(base_thickness)) as hs:
        RegularPolygon(hex_radius, 6)
    extrude(amount=hex_height, taper=-draft_angle)

solid_body = solid_body + hex_p.part

solid_body = solid_body - Pos(0, 0, (base_thickness + hex_height)/2) * Cylinder(central_hole_radius, base_thickness + hex_height + 1)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "base_plate_with_hex_boss"
export_step(part, "output.step")
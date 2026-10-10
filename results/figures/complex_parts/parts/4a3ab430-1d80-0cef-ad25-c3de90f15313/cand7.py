from build123d import *

base_width = 80.0
base_length = 80.0
base_thickness = 5.0
hex_radius = 30.0
circle_radius = 20.0
loft_height = 20.0
chamfer_distance = 2.0
mount_hole_dia = 5.0
mount_hole_offset = 30.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(base_width, base_length)
    extrude(amount=base_thickness)

solid_body = p.part

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (-mount_hole_offset, -mount_hole_offset), (mount_hole_offset, -mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, base_thickness/2) * Cylinder(mount_hole_dia/2, base_thickness + 1)

with BuildPart() as loft_p:
    with BuildSketch(Plane.XY.offset(base_thickness)) as s1:
        RegularPolygon(hex_radius, 6)
    with BuildSketch(Plane.XY.offset(base_thickness + loft_height)) as s2:
        Circle(circle_radius)
    loft()

solid_body = solid_body + loft_p.part

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "base_plate_with_loft"
export_step(part, "output.step")
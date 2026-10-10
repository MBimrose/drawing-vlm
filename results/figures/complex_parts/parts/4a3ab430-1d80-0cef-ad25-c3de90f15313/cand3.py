from build123d import *

base_length = 80.0
base_width = 80.0
base_thickness = 5.0
hex_radius = 30.0
circle_radius = 25.0
loft_height = 20.0
chamfer_dist = 2.0
mount_hole_dia = 5.0
mount_hole_offset = 30.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)

with BuildPart() as p:
    with BuildSketch(Plane.XY.offset(base_thickness)) as s1:
        RegularPolygon(hex_radius, 6)
    with BuildSketch(Plane.XY.offset(base_thickness + loft_height)) as s2:
        Circle(circle_radius)
    loft()
loft_body = p.part

result = base + loft_body
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_dist)

hole_positions = [
    (mount_hole_offset, mount_hole_offset),
    (-mount_hole_offset, mount_hole_offset),
    (-mount_hole_offset, -mount_hole_offset),
    (mount_hole_offset, -mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, 100)

part = result
part.name = "lofted_base_with_mount_holes"
export_step(part, "output.step")
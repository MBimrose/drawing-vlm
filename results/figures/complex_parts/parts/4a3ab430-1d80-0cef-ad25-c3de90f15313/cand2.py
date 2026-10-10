from build123d import *

base_length = 80.0
base_width = 80.0
base_thickness = 5.0
hex_radius = 30.0
hex_height = 20.0
top_radius = 20.0
chamfer_distance = 2.0
mount_hole_dia = 5.0
mount_hole_offset = 10.0

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)

with BuildPart() as p:
    with BuildSketch() as s1:
        RegularPolygon(hex_radius, 6)
    with BuildSketch(Plane.XY.offset(hex_height)) as s2:
        Circle(top_radius)
    loft()
hex_loft = Pos(0, 0, base_thickness) * p.part

result = base + hex_loft
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

hole_positions = [
    (base_length/2 - mount_hole_offset, base_width/2 - mount_hole_offset),
    (-base_length/2 + mount_hole_offset, base_width/2 - mount_hole_offset),
    (-base_length/2 + mount_hole_offset, -base_width/2 + mount_hole_offset),
    (base_length/2 - mount_hole_offset, -base_width/2 + mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, base_thickness/2) * Cylinder(mount_hole_dia/2, base_thickness + 1)

part = result
part.name = "base_with_hex_loft"
export_step(part, "output.step")
from build123d import *

plate_width = 80.0
plate_depth = 80.0
plate_thickness = 5.0
hex_radius = 30.0
circle_radius = 20.0
loft_height = 20.0
chamfer_size = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0

base = Pos(0, 0, plate_thickness / 2) * Box(plate_width, plate_depth, plate_thickness)

with BuildPart() as p:
    with BuildSketch(Plane.XY.offset(plate_thickness)) as s1:
        RegularPolygon(hex_radius, 6)
    with BuildSketch(Plane.XY.offset(plate_thickness + loft_height)) as s2:
        Circle(circle_radius)
    loft()
loft_body = p.part

result = base + loft_body
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

hole_positions = [
    (plate_width/2 - mount_hole_offset, plate_depth/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, plate_depth/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, -plate_depth/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, -plate_depth/2 + mount_hole_offset),
]

for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, 100)

part = result
part.name = "plate_with_loft_and_holes"
export_step(part, "output.step")
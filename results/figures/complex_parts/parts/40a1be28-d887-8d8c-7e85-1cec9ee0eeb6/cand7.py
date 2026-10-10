from build123d import *

base_diameter = 40.0
base_height = 20.0
transition_height = 12.0
top_width = 60.0
top_length = 40.0
top_thickness = 8.0
central_hole_diameter = 8.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_diameter / 2)
    with BuildSketch(Plane.XY.offset(base_height)) as s2:
        Circle((base_diameter / 2) * 0.6)
    with BuildSketch(Plane.XY.offset(base_height + transition_height)) as s3:
        Rectangle(top_width, top_length)
    loft()

solid_body = p.part
solid_body = solid_body + Pos(0, 0, base_height + transition_height + top_thickness / 2) * Box(top_width, top_length, top_thickness)

total_height = base_height + transition_height + top_thickness
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(central_hole_diameter / 2, total_height + 10)

mount_points = [
    (-top_width / 2 + mount_hole_offset, -top_length / 2 + mount_hole_offset),
    (top_width / 2 - mount_hole_offset, -top_length / 2 + mount_hole_offset),
    (-top_width / 2 + mount_hole_offset, top_length / 2 - mount_hole_offset),
    (top_width / 2 - mount_hole_offset, top_length / 2 - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, total_height / 2) * Cylinder(mount_hole_diameter / 2, total_height + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "lofted_base_with_mounting_plate"
export_step(part, "output.step")
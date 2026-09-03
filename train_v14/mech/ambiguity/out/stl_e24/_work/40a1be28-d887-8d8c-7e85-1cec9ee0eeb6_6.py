from build123d import *

base_radius = 20.0
mid_radius = 15.0
top_width = 60.0
top_length = 40.0
total_height = 40.0
mid_height = 12.0
pad_thickness = 8.0
central_hole_diameter = 8.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(mid_height)) as s2:
        Circle(mid_radius)
    with BuildSketch(Plane.XY.offset(total_height - pad_thickness)) as s3:
        Rectangle(top_width, top_length)
    loft()

solid_body = p.part
pad = Pos(0, 0, total_height - pad_thickness / 2) * Box(top_width, top_length, pad_thickness)
solid_body = solid_body + pad

hole_h = total_height + 20
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(central_hole_diameter / 2, hole_h)

for x, y in [
    (-top_width / 2 + mount_hole_offset, -top_length / 2 + mount_hole_offset),
    (top_width / 2 - mount_hole_offset, -top_length / 2 + mount_hole_offset),
    (top_width / 2 - mount_hole_offset, top_length / 2 - mount_hole_offset),
    (-top_width / 2 + mount_hole_offset, top_length / 2 - mount_hole_offset),
]:
    solid_body = solid_body - Pos(x, y, total_height / 2) * Cylinder(mount_hole_diameter / 2, hole_h)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "lofted_pad_with_holes"
export_step(part, "output.step")
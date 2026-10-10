from build123d import *

base_radius = 20.0
mid_radius = 15.0
top_radius = 10.0
loft_height = 30.0
mid_height = loft_height / 2.0
top_height = loft_height
flange_width = 60.0
flange_length = 40.0
flange_thickness = 8.0
hole_diameter = 8.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(mid_height)) as s2:
        Circle(mid_radius)
    with BuildSketch(Plane.XY.offset(top_height)) as s3:
        Circle(top_radius)
    loft()

solid_body = p.part
flange = Pos(0, 0, top_height + flange_thickness / 2) * Box(flange_width, flange_length, flange_thickness)
solid_body = solid_body + flange

total_height = top_height + flange_thickness
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(hole_diameter / 2, total_height + 10)

mount_points = [
    (-flange_width / 2 + mount_hole_offset, -flange_length / 2 + mount_hole_offset),
    (flange_width / 2 - mount_hole_offset, -flange_length / 2 + mount_hole_offset),
    (-flange_width / 2 + mount_hole_offset, flange_length / 2 - mount_hole_offset),
    (flange_width / 2 - mount_hole_offset, flange_length / 2 - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, total_height / 2) * Cylinder(mount_hole_diameter / 2, total_height + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "lofted_flange_with_holes"
export_step(part, "output.step")
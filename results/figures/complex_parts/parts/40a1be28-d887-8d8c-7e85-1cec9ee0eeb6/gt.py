from build123d import *

base_radius = 20.0
neck_length = 40.0
intermediate_radius = 12.0
flange_width = 60.0
flange_height = 40.0
flange_thickness = 8.0
thread_diameter = 8.0
thread_length = 30.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_size = 1.0

z1 = neck_length * 0.5
z2 = z1 + neck_length * 0.5 - flange_thickness
total_height = z2 + flange_thickness

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(z1)) as s2:
        Circle(intermediate_radius)
    with BuildSketch(Plane.XY.offset(z2)) as s3:
        Rectangle(flange_width - 2 * chamfer_size, flange_height - 2 * chamfer_size)
    loft()

solid_body = p.part

with BuildPart() as fp:
    with BuildSketch(Plane.XY.offset(z2)) as fs:
        Rectangle(flange_width, flange_height)
    extrude(amount=flange_thickness)
solid_body = solid_body + fp.part

hole_h = total_height + 20
hole_z = total_height / 2
solid_body = solid_body - Pos(0, 0, hole_z) * Cylinder(thread_diameter / 2, hole_h)

mount_points = [
    (-flange_width/2 + mount_hole_offset, -flange_height/2 + mount_hole_offset),
    (flange_width/2 - mount_hole_offset, -flange_height/2 + mount_hole_offset),
    (-flange_width/2 + mount_hole_offset, flange_height/2 - mount_hole_offset),
    (flange_width/2 - mount_hole_offset, flange_height/2 - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, hole_z) * Cylinder(mount_hole_diameter / 2, hole_h)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "flanged_neck_with_mounting_holes"
export_step(part, OUTPUT_PATH)
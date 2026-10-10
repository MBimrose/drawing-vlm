from build123d import *

base_radius = 20.0
shaft_radius = 7.5
top_radius = 15.0
base_height = 10.0
shaft_height = 20.0
top_height = 10.0
plate_width = 60.0
plate_depth = 40.0
plate_thickness = 8.0
central_hole_diameter = 8.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_distance = 1.0

total_height = base_height + shaft_height + top_height

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(base_height)) as s2:
        Circle(shaft_radius)
    with BuildSketch(Plane.XY.offset(base_height + shaft_height)) as s3:
        Circle(top_radius)
    loft()

solid_body = p.part

plate = Pos(0, 0, total_height + plate_thickness / 2) * Box(plate_width, plate_depth, plate_thickness)
solid_body = solid_body + plate

hole_height = total_height + plate_thickness + 20
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(central_hole_diameter / 2, hole_height)

mount_points = [
    (-plate_width / 2 + mount_hole_offset, -plate_depth / 2 + mount_hole_offset),
    (plate_width / 2 - mount_hole_offset, -plate_depth / 2 + mount_hole_offset),
    (-plate_width / 2 + mount_hole_offset, plate_depth / 2 - mount_hole_offset),
    (plate_width / 2 - mount_hole_offset, plate_depth / 2 - mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, total_height + plate_thickness / 2) * Cylinder(mount_hole_diameter / 2, plate_thickness + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "lofted_shaft_with_plate"
export_step(part, "output.step")
from build123d import *

base_radius = 20.0
mid_radius = 10.0
top_radius = 15.0
total_height = 40.0
mid_height = total_height * 0.5
top_height = total_height * 0.8
plate_width = 60.0
plate_length = 40.0
plate_thickness = 8.0
central_hole_diameter = 8.0
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
loft_body = p.part

plate = Pos(0, 0, top_height + plate_thickness / 2) * Box(plate_width, plate_length, plate_thickness)
result = loft_body + plate

result = result - Pos(0, 0, total_height / 2) * Cylinder(central_hole_diameter / 2, total_height + 10)

mount_points = [
    (-plate_width/2 + mount_hole_offset, -plate_length/2 + mount_hole_offset),
    ( plate_width/2 - mount_hole_offset, -plate_length/2 + mount_hole_offset),
    (-plate_width/2 + mount_hole_offset,  plate_length/2 - mount_hole_offset),
    ( plate_width/2 - mount_hole_offset,  plate_length/2 - mount_hole_offset),
]
for x, y in mount_points:
    result = result - Pos(x, y, total_height / 2) * Cylinder(mount_hole_diameter / 2, total_height + 10)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)
top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "lofted_plate_with_holes"
export_step(part, "output.step")
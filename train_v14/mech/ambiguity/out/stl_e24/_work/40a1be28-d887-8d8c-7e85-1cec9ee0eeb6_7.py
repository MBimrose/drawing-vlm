from build123d import *

base_radius = 20.0
mid_radius = 10.0
top_width = 60.0
top_depth = 40.0
total_height = 40.0
mid_height = total_height * 0.5
top_thickness = 8.0
central_hole_diameter = 8.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(mid_height)) as s2:
        Circle(mid_radius)
    with BuildSketch(Plane.XY.offset(total_height)) as s3:
        Rectangle(top_width, top_depth)
    loft()

solid_body = p.part
solid_body = solid_body + Pos(0, 0, total_height - top_thickness/2) * Box(top_width, top_depth, top_thickness)
solid_body = solid_body - Pos(0, 0, total_height/2) * Cylinder(central_hole_diameter/2, total_height + 10)

mount_points = [
    (-top_width/2 + mount_hole_offset, -top_depth/2 + mount_hole_offset),
    ( top_width/2 - mount_hole_offset, -top_depth/2 + mount_hole_offset),
    ( top_width/2 - mount_hole_offset,  top_depth/2 - mount_hole_offset),
    (-top_width/2 + mount_hole_offset,  top_depth/2 - mount_hole_offset)
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, total_height - top_thickness/2) * Cylinder(mount_hole_diameter/2, top_thickness + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "lofted_body_with_holes"
export_step(part, "output.step")
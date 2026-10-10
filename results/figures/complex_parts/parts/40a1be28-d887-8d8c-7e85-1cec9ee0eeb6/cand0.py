from build123d import *

base_diameter = 40.0
base_height = 10.0
transition_height = 30.0
top_width = 60.0
top_length = 40.0
top_thickness = 8.0
central_hole_diameter = 8.0
mount_hole_diameter = 5.0
mount_hole_spacing_x = 40.0
mount_hole_spacing_y = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_diameter / 2)
    with BuildSketch(Plane.XY.offset(base_height)) as s2:
        Circle(base_diameter / 2 * 0.6)
    with BuildSketch(Plane.XY.offset(base_height + transition_height)) as s3:
        Rectangle(top_width, top_length)
    loft()

solid_body = p.part
top_box = Pos(0, 0, base_height + transition_height + top_thickness / 2) * Box(top_width, top_length, top_thickness)
solid_body = solid_body + top_box

total_height = base_height + transition_height + top_thickness
hole_height = total_height + 20
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(central_hole_diameter / 2, hole_height)

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, total_height / 2) * Cylinder(mount_hole_diameter / 2, hole_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "lofted_base_with_mounting_holes"
export_step(part, "output.step")
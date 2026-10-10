from build123d import *

circle_diameter = 40.0
rect_width = 60.0
rect_height = 40.0
loft_length = 40.0
central_hole_diameter = 8.0
mount_hole_diameter = 5.0
mount_hole_spacing_x = 40.0
mount_hole_spacing_y = 20.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(circle_diameter / 2)
    with BuildSketch(Plane.XY.offset(loft_length)) as s2:
        Rectangle(rect_width, rect_height)
    loft()

solid_body = p.part
solid_body = solid_body - Cylinder(central_hole_diameter / 2, loft_length * 2)

for x, y in [(-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
             (-mount_hole_spacing_x/2, mount_hole_spacing_y/2),
             (mount_hole_spacing_x/2, mount_hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, loft_length * 2)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "lofted_transition_with_holes"
export_step(part, "output.step")
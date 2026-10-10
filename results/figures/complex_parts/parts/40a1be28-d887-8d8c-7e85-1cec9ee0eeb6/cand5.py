from build123d import *

base_diameter = 40.0
top_width = 60.0
top_length = 40.0
total_height = 40.0
flange_thickness = 8.0
central_hole_diameter = 8.0
mount_hole_diameter = 5.0
mount_hole_spacing_x = 40.0
mount_hole_spacing_y = 20.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_diameter / 2)
    with BuildSketch(Plane.XY.offset(total_height - flange_thickness)) as s2:
        Rectangle(top_width, top_length)
    loft()

solid_body = p.part
flange = Pos(0, 0, total_height - flange_thickness / 2) * Box(top_width, top_length, flange_thickness)
solid_body = solid_body + flange

solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(central_hole_diameter / 2, total_height + 10)

for x, y in [(-mount_hole_spacing_x / 2, -mount_hole_spacing_y / 2),
             (mount_hole_spacing_x / 2, -mount_hole_spacing_y / 2),
             (-mount_hole_spacing_x / 2, mount_hole_spacing_y / 2),
             (mount_hole_spacing_x / 2, mount_hole_spacing_y / 2)]:
    solid_body = solid_body - Pos(x, y, total_height / 2) * Cylinder(mount_hole_diameter / 2, total_height + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "lofted_flange_with_holes"
export_step(part, "output.step")
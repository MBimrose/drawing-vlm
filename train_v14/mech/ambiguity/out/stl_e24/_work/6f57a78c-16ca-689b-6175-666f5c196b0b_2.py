from build123d import *

outer_diameter = 80.0
inner_diameter = 60.0
length = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
groove_width = 10.0
groove_depth = 5.0
mount_hole_diameter = 6.0
mount_hole_spacing = 45.0
chamfer_size = 1.0

outer_cyl = Cylinder(outer_diameter / 2.0, length)
inner_cyl = Cylinder(inner_diameter / 2.0, length)
result = outer_cyl - inner_cyl

groove = Pos(0, 0, groove_width / 2.0) * Cylinder((inner_diameter / 2.0) - groove_depth, groove_width)
result = result - groove

for y in [-mount_hole_spacing / 2.0, mount_hole_spacing / 2.0]:
    hole = Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2.0, wall_thickness * 2.0)
    result = result - hole

result = chamfer(result.edges(), chamfer_size)

part = result
part.name = "hollow_cylinder_with_groove_and_mount_holes"
export_step(part, "output.step")
from build123d import *

arm_length = 80.0
arm_width = 40.0
arm_height = 20.0
wall_thickness = 3.0
rib_thickness = 2.0
rib_height = 10.0
rib_spacing = 10.0
rib_count = 3
chamfer_distance = 1.0
mount_hole_diameter = 4.0
mount_hole_spacing_x = 30.0
mount_hole_spacing_y = 20.0

solid_body = Box(arm_width, arm_height, arm_length)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

inner_width = arm_width - 2 * wall_thickness
inner_height = arm_height - 2 * wall_thickness
inner_length = arm_length - wall_thickness
cavity = Pos(0, 0, -wall_thickness / 2) * Box(inner_width, inner_height, inner_length)
solid_body = solid_body - cavity

for i in range(rib_count):
    x_offset = -inner_width / 2 + wall_thickness + rib_spacing / 2 + i * rib_spacing
    rib = Pos(x_offset, 0, -arm_length / 2 + inner_length / 2) * Box(rib_thickness, rib_height, inner_length)
    solid_body = solid_body + rib

for x, y in [(-mount_hole_spacing_x / 2, -mount_hole_spacing_y / 2),
             (mount_hole_spacing_x / 2, -mount_hole_spacing_y / 2),
             (-mount_hole_spacing_x / 2, mount_hole_spacing_y / 2),
             (mount_hole_spacing_x / 2, mount_hole_spacing_y / 2)]:
    hole = Pos(x, y, arm_length / 2) * Cylinder(mount_hole_diameter / 2, arm_length)
    solid_body = solid_body - hole

part = solid_body
part.name = "arm_with_ribs"
export_step(part, "output.step")
from build123d import *
import math

inner_diameter = 20.0
outer_diameter = 36.0
collar_length = 30.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
groove_width = 2.0
groove_depth = 2.4
groove_position = 12.0
chamfer_size = 0.5
mount_hole_diameter = 4.0
mount_hole_count = 3
mount_hole_radius = (outer_diameter / 2.0) - wall_thickness / 2.0
keyway_width = 4.0
keyway_depth = 2.0
keyway_length = collar_length * 0.4

solid_body = Cylinder(outer_diameter / 2.0, collar_length) - Cylinder(inner_diameter / 2.0, collar_length)

groove = Pos(inner_diameter / 2.0 + groove_depth / 2.0, 0, groove_position) * Cylinder(groove_depth / 2.0, groove_width)
solid_body = solid_body - groove

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, collar_length / 2.0) * Cylinder(mount_hole_diameter / 2.0, collar_length + 2)

keyway = Pos(inner_diameter / 2.0 + keyway_depth / 2.0, 0, collar_length / 2.0) * Box(keyway_depth, keyway_width, keyway_length)
solid_body = solid_body - keyway

part = solid_body
part.name = "collar_with_groove_and_keyway"
export_step(part, "output.step")
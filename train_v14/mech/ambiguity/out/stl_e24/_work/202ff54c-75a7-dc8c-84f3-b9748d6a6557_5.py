from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
height = 60.0
wall_thickness = (outer_diameter - inner_diameter) / 2
rib_thickness = 3.0
rib_width = 6.0
rib_height = 30.0
rib_count = 4
keyway_width = 12.0
keyway_depth = wall_thickness * 0.6
keyway_length = 20.0
mount_hole_dia = 4.0
mount_hole_spacing = 30.0
chamfer_size = 2.0

solid_body = Cylinder(outer_diameter / 2, height) - Cylinder(inner_diameter / 2, height)

rib_radius = outer_diameter / 2 - rib_thickness / 2
for i in range(rib_count):
    angle = math.radians(i * 360.0 / rib_count)
    px = rib_radius * math.cos(angle)
    py = rib_radius * math.sin(angle)
    solid_body = solid_body + Pos(px, py, 0) * Box(rib_thickness, rib_width, rib_height)

solid_body = solid_body - Pos(outer_diameter / 2 - keyway_depth / 2, 0, 0) * Box(keyway_depth, keyway_width, keyway_length)

hole_radius = outer_diameter / 2 - wall_thickness / 2
for i in range(2):
    angle = math.radians(i * 180.0)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mount_hole_dia / 2, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "ribbed_cylinder_with_keyway"
export_step(part, "output.step")
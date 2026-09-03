from build123d import *

outer_diameter = 80.0
inner_diameter = 40.0
length = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
relief_hole_diameter = 8.0
relief_hole_offset = 30.0
chamfer_distance = 1.5
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
rib_thickness = 4.0
rib_height = 6.0
rib_count = 4
boss_width = 10.0
boss_length = 20.0
boss_height = 5.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

solid_body = solid_body - Pos(relief_hole_offset, 0, 0) * Cylinder(relief_hole_diameter / 2, length)

mount_points = [
    (mount_hole_spacing / 2.0, mount_hole_spacing / 2.0),
    (-mount_hole_spacing / 2.0, mount_hole_spacing / 2.0),
    (-mount_hole_spacing / 2.0, -mount_hole_spacing / 2.0),
    (mount_hole_spacing / 2.0, -mount_hole_spacing / 2.0),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, length)

rib = Pos(inner_radius + wall_thickness / 2.0, 0, 0) * Box(wall_thickness, rib_thickness, rib_height)
ribs = rib
for i in range(1, rib_count):
    angle = 360.0 / rib_count * i
    ribs = ribs + Rot(0, 0, angle) * rib
solid_body = solid_body + ribs

boss = Pos(0, 0, length / 2.0 + boss_height / 2.0) * Box(boss_width, boss_length, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "hollow_cylinder_with_features"
export_step(part, "output.step")
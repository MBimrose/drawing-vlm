from build123d import *

outer_diameter = 80.0
inner_diameter = 40.0
length = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
chamfer_size = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 15.0
lub_hole_diameter = 8.0
lub_hole_offset = 30.0
rib_thickness = 4.0
rib_height = 6.0
boss_width = 10.0
boss_length = 20.0
boss_height = 5.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

mount_points = [
    (mount_hole_offset, mount_hole_offset),
    (-mount_hole_offset, mount_hole_offset),
    (-mount_hole_offset, -mount_hole_offset),
    (mount_hole_offset, -mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, length)

solid_body = solid_body - Pos(lub_hole_offset, 0, 0) * Cylinder(lub_hole_diameter / 2, length)

rib = Pos(inner_radius + rib_thickness / 2.0, 0, 0) * Box(rib_thickness, length, rib_height)
rib_pair = rib + Rot(0, 0, 180) * rib
solid_body = solid_body + rib_pair

boss = Pos(0, 0, length / 2 + boss_height / 2) * Box(boss_width, boss_length, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "hollow_cylinder_with_ribs_and_boss"
export_step(part, "output.step")
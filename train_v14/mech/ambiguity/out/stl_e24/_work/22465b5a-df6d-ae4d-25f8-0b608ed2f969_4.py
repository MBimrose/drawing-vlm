from build123d import *

outer_diameter = 60
wall_thickness = 5
length = 80
chamfer_size = 2
mount_hole_diameter = 4
mount_hole_spacing = 30
boss_diameter = 20
boss_thickness = 6
boss_offset = 10

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

hole_positions = [
    (-mount_hole_spacing / 2, -mount_hole_spacing / 2),
    (mount_hole_spacing / 2, -mount_hole_spacing / 2),
    (-mount_hole_spacing / 2, mount_hole_spacing / 2),
    (mount_hole_spacing / 2, mount_hole_spacing / 2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter / 2, length)

boss = Pos(outer_radius + boss_thickness / 2, 0, -length / 2 + boss_offset) * Rot(0, 90, 0) * Cylinder(boss_diameter / 2, boss_thickness)
solid_body = solid_body + boss

part = solid_body
part.name = "hollow_cylinder_with_boss"
export_step(part, "output.step")
from build123d import *
import math

outer_diameter = 60.0
wall_thickness = 5.0
length = 80.0
rib_width = 6.0
rib_height = 8.0
rib_count = 12
groove_width = 5.0
groove_depth = 3.0
boss_diameter = 20.0
boss_length = 30.0
boss_hole_diameter = 10.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

rib = Pos(outer_radius + rib_height / 2.0, 0, 0) * Box(rib_width, rib_height, length)
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    solid_body = solid_body + Rot(0, 0, angle) * rib

groove = Pos(0, 0, length - groove_width / 2.0) * Cylinder(outer_radius - groove_depth, groove_width)
solid_body = solid_body - groove

boss = Pos(0, 0, -length / 2.0 - boss_length / 2.0) * Cylinder(boss_diameter / 2.0, boss_length)
solid_body = solid_body + boss

hole = Pos(0, 0, -length / 2.0 - boss_length / 2.0) * Cylinder(boss_hole_diameter / 2.0, boss_length)
solid_body = solid_body - hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")
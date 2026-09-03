from build123d import *

outer_radius = 30.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
body_length = 80.0
rib_height = 6.0
rib_width = 8.0
rib_count = 12
boss_radius = 10.0
boss_length = 30.0
blind_hole_diameter = 6.0
blind_hole_depth = 20.0
chamfer_size = 1.0

import math

solid_body = Cylinder(outer_radius, body_length) - Cylinder(inner_radius, body_length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius + rib_height / 2.0, 0, 0) * Box(rib_height, rib_width, body_length)
    solid_body = solid_body + rib

boss = Pos(0, 0, -body_length / 2.0 - boss_length / 2.0) * Cylinder(boss_radius, boss_length)
solid_body = solid_body + boss

hole = Pos(0, 0, -body_length / 2.0 - boss_length + blind_hole_depth / 2.0) * Cylinder(blind_hole_diameter / 2.0, blind_hole_depth)
solid_body = solid_body - hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "ribbed_cylinder_with_boss"
export_step(part, "output.step")
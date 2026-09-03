from build123d import *
import math

outer_diameter = 60.0
wall_thickness = 5.0
length = 80.0
rib_width = 6.0
rib_height = 8.0
rib_count = 12
boss_diameter = 20.0
boss_height = 30.0
thread_diameter = 10.0
thread_depth = 20.0
chamfer_distance = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
boss_radius = boss_diameter / 2.0

solid_body = Pos(0, 0, length / 2) * Cylinder(outer_radius, length)
solid_body = solid_body - Pos(0, 0, length / 2) * Cylinder(inner_radius, length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius + rib_height / 2.0, 0, length / 2) * Box(rib_width, rib_height, length)
    solid_body = solid_body + rib

solid_body = solid_body + Pos(0, 0, -boss_height / 2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body - Pos(0, 0, -thread_depth / 2) * Cylinder(thread_diameter / 2.0, thread_depth)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

part = solid_body
part.name = "ribbed_cylinder_with_boss"
export_step(part, "output.step")
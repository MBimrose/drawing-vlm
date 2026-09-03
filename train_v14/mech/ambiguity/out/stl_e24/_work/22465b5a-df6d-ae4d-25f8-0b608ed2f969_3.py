from build123d import *
import math

outer_radius = 30.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
length = 80.0
boss_radius = 10.0
boss_height = 6.0
boss_center_z = 15.0
chamfer_size = 2.0
groove_depth = 2.0
groove_width = 4.0
groove_center_z = 30.0
mount_hole_diameter = 4.0
mount_hole_radius = (inner_radius + outer_radius) / 2.0

shell = Pos(0, 0, length/2) * (Cylinder(outer_radius, length) - Cylinder(inner_radius, length))
boss = Pos(outer_radius + boss_height/2, 0, boss_center_z) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
result = shell + boss

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

groove = Pos(0, 0, groove_center_z) * Cylinder(outer_radius - groove_depth, groove_width)
result = result - groove

for angle in [0, 90, 180, 270]:
    rad = math.radians(angle)
    x = mount_hole_radius * math.cos(rad)
    y = mount_hole_radius * math.sin(rad)
    hole = Pos(x, y, length/2) * Cylinder(mount_hole_diameter/2, length)
    result = result - hole

part = result
part.name = "cylindrical_shell_with_boss"
export_step(part, "output.step")
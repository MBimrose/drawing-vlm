from build123d import *
import math

outer_diameter = 80.0
cap_height = 30.0
wall_thickness = 2.0
boss_diameter = 20.0
boss_height = 10.0
rib_count = 8
rib_thickness = 4.0
rib_height = 10.0
chamfer_size = 0.5
mount_hole_diameter = 5.0
mount_hole_offset = 20.0

outer_radius = outer_diameter / 2.0
boss_radius = boss_diameter / 2.0

solid_body = Cylinder(outer_radius, cap_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

solid_body = solid_body + Cylinder(boss_radius, boss_height)

rib = Box(rib_thickness, rib_height, wall_thickness)
rib = Pos(outer_radius - wall_thickness - rib_thickness/2, 0, cap_height/2) * rib
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

for x, y in [(mount_hole_offset, 0), (-mount_hole_offset, 0)]:
    hole = Pos(x, y, cap_height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, outer_diameter)
    solid_body = solid_body - hole

part = solid_body
part.name = "cap_with_boss_and_ribs"
export_step(part, "output.step")
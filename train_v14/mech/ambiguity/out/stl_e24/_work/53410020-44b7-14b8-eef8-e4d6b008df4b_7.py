from build123d import *
import math

outer_diameter = 60.0
thickness = 12.0
keyway_width = 6.0
keyway_length = 20.0
fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 25.0
rib_width = 4.0
rib_height = 2.0
rib_count = 6
boss_diameter = 20.0
boss_height = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

keyway = Pos(outer_diameter / 2 - keyway_length / 2, 0, thickness / 2) * Box(keyway_length, keyway_width, thickness)
solid_body = solid_body - keyway

for i in range(4):
    a = math.radians(i * 90)
    px = mount_hole_offset * math.cos(a)
    py = mount_hole_offset * math.sin(a)
    solid_body = solid_body - Pos(px, py, thickness / 2) * Cylinder(mount_hole_diameter / 2, thickness)

for i in range(rib_count):
    a = math.radians(i * 360 / rib_count)
    rib = Rot(0, 0, a) * Pos(outer_diameter / 2 - rib_height / 2, 0, thickness / 2) * Box(rib_height, rib_width, thickness)
    solid_body = solid_body + rib

boss = Pos(0, 0, boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "flanged_disc_with_ribs"
export_step(part, "output.step")
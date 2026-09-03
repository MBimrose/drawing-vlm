from build123d import *
import math

outer_radius = 45
inner_radius = 15
thickness = 5
boss_radius = 15
boss_height = 2
central_hole_dia = 9
slot_width = 6
slot_length = 20
slot_offset = 30
mount_hole_dia = 5
mount_hole_radius = 36
mount_hole_count = 3
chamfer_dist = 1

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
        Circle(inner_radius, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, thickness/2) * Cylinder(central_hole_dia/2, thickness)

solid_body = solid_body + Pos(0, 0, boss_height/2) * Cylinder(boss_radius, boss_height)

solid_body = solid_body - Pos(slot_offset, 0, thickness/2) * Box(slot_width, slot_length, thickness)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness/2) * Cylinder(mount_hole_dia/2, thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_dist)

part = solid_body
part.name = "flanged_disc_with_boss"
export_step(part, "output.step")
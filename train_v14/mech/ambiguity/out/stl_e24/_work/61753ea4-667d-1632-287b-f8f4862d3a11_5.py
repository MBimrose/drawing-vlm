from build123d import *
import math

outer_diameter = 80.0
thickness = 10.0
central_hole_diameter = 30.0
slot_width = 5.0
slot_length = 70.0
chamfer_distance = 1.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
mount_hole_offset = 10.0
boss_diameter = 20.0
boss_height = 5.0
rib_width = 5.0
rib_height = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=thickness)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, thickness / 2) * Cylinder(central_hole_diameter / 2, thickness)

solid_body = solid_body - Pos(0, 0, thickness / 2) * Box(slot_length, slot_width, thickness)

mount_points = [
    (-mount_hole_offset, mount_hole_spacing / 2),
    (-mount_hole_offset, -mount_hole_spacing / 2),
    (mount_hole_offset, mount_hole_spacing / 2),
    (mount_hole_offset, -mount_hole_spacing / 2),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(mount_hole_diameter / 2, thickness)

solid_body = solid_body + Pos(0, 0, boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

solid_body = solid_body + Pos(0, 0, rib_height / 2) * Box(rib_width, outer_diameter - 2 * mount_hole_offset, rib_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "flanged_disc_with_boss_and_rib"
export_step(part, "output.step")
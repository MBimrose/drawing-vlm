from build123d import *

block_length = 60.0
block_width = 40.0
block_height = 20.0
central_hole_dia = 20.0
boss_radius = 12.0
boss_height = 5.0
fillet_radius = 2.0
mount_hole_dia = 6.0
mount_hole_spacing = 30.0
slot_width = 15.0
slot_length = 20.0
slot_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_height)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = solid_body - Cylinder(central_hole_dia / 2, block_height * 2)
solid_body = solid_body + Pos(0, 0, block_height + boss_height / 2) * Cylinder(boss_radius, boss_height)

mount_pts = [
    (-mount_hole_spacing / 2, -mount_hole_spacing / 2),
    (mount_hole_spacing / 2, -mount_hole_spacing / 2),
    (-mount_hole_spacing / 2, mount_hole_spacing / 2),
    (mount_hole_spacing / 2, mount_hole_spacing / 2),
]
for x, y in mount_pts:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_dia / 2, block_height * 2)

slot_y = block_width / 2 - slot_offset
solid_body = solid_body - Pos(0, slot_y, block_height - slot_offset / 2) * Box(slot_width, slot_length, slot_offset)

part = solid_body
part.name = "block_with_boss_and_holes"
export_step(part, "output.step")
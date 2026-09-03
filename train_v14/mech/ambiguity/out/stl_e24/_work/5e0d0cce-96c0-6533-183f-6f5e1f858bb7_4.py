from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
boss_diameter = 12.0
boss_height = 12.0
slot_width = 10.0
slot_length = 30.0
slot_offset = 5.0
chamfer_dist = 1.0
fillet_radius = 0.5
mount_hole_dia = 5.0
mount_hole_offset = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_width, block_length)
    extrude(amount=block_height)

solid_body = p.part
solid_body = solid_body + Pos(0, 0, block_height) * Cylinder(boss_diameter/2, boss_height)

slot_center_y = block_width/2 - slot_offset - slot_width/2
slot_cut = Pos(0, slot_center_y, block_height/2) * Box(slot_width, slot_length, block_height)
solid_body = solid_body - slot_cut

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_dist)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

px = block_width/2 - mount_hole_offset - mount_hole_dia/2
py = block_length/2 - mount_hole_offset - mount_hole_dia/2
for x, y in [(px, py), (-px, py), (-px, -py), (px, -py)]:
    solid_body = solid_body - Pos(x, y, block_height/2) * Cylinder(mount_hole_dia/2, block_height)

part = solid_body
part.name = "block_with_boss_slot_and_holes"
export_step(part, "output.step")
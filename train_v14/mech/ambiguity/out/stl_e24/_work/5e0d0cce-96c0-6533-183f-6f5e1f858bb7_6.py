from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
slot_width = 10.0
slot_length = 30.0
slot_offset = 5.0
boss_diameter = 12.0
boss_height = 12.0
fillet_radius = 1.0
chamfer_distance = 0.8
mount_hole_diameter = 5.0
mount_hole_offset = 5.0
rib_width = 5.0
rib_length = 30.0
rib_height = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_width, block_length)
    extrude(amount=block_height)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

slot_cut = Pos(0, slot_offset, block_height/2) * Box(slot_width, slot_length, block_height)
solid_body = solid_body - slot_cut

boss = Pos(0, 0, block_height) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

px = block_width/2 - mount_hole_offset - mount_hole_diameter/2
py = block_length/2 - mount_hole_offset - mount_hole_diameter/2
for x, y in [(px, py), (-px, py), (-px, -py), (px, -py)]:
    solid_body = solid_body - Pos(x, y, block_height/2) * Cylinder(mount_hole_diameter/2, block_height)

rib1 = Pos(-block_width/4, 0, block_height + rib_height/2) * Box(rib_width, rib_length, rib_height)
rib2 = Pos(block_width/4, 0, block_height + rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "block_with_slot_boss_ribs"
export_step(part, "output.step")
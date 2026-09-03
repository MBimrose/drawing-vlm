from build123d import *

block_width = 80
block_depth = 50
block_height = 60
boss_radius = 10
boss_height = 10
through_hole_radius = 8
fillet_radius = 3
chamfer_distance = 2
mount_hole_radius = 2.5
mount_hole_spacing = 30

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_width, block_depth)
    extrude(amount=block_height)
    with BuildSketch() as s2:
        Circle(boss_radius)
    extrude(amount=boss_height)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, (block_height + boss_height)/2) * Cylinder(through_hole_radius, block_height + boss_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, block_height) * Rot(90, 0, 0) * Cylinder(mount_hole_radius, block_depth)

part = solid_body
part.name = "block_with_boss_and_holes"
export_step(part, "output.step")
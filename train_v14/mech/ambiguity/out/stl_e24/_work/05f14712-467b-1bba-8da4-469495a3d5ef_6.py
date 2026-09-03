from build123d import *

block_width = 70
block_depth = 50
block_height = 30
rib_width = 10
rib_height = 5
rib_length = block_width
hole_diameter = 12
hole_spacing = 30
fillet_radius = 1
chamfer_distance = 1
mount_hole_diameter = 4
mount_hole_offset = 10
pocket_width = 30
pocket_depth = 20
pocket_height = 10
side_hole_diameter = 6
side_hole_offset = 10

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_width, block_depth)
    extrude(amount=block_height)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

rib = Pos(0, 0, block_height/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, block_height * 2)

mount_points = [
    (-block_width/2 + mount_hole_offset, -block_depth/2 + mount_hole_offset),
    ( block_width/2 - mount_hole_offset, -block_depth/2 + mount_hole_offset),
    ( block_width/2 - mount_hole_offset,  block_depth/2 - mount_hole_offset),
    (-block_width/2 + mount_hole_offset,  block_depth/2 - mount_hole_offset)
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height * 2)

pocket = Pos(0, 0, pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

side_hole = Pos(block_width/2, 0, block_height/2 + side_hole_offset) * Rot(0, 90, 0) * Cylinder(side_hole_diameter/2, block_width * 2)
solid_body = solid_body - side_hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

part = solid_body
part.name = "block_with_rib_and_holes"
export_step(part, "output.step")
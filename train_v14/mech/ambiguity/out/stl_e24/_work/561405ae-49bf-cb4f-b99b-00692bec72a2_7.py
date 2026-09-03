from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
boss_diameter = 20.0
boss_height = 10.0
central_hole_dia = 12.0
mount_hole_dia = 6.0
mount_hole_spacing = 30.0
mount_hole_offset = 15.0
fillet_radius = 4.0
chamfer_distance = 2.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 8.0
pocket_offset = 15.0
counterbore_dia = 10.0
counterbore_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_height)
    with BuildSketch() as s2:
        Circle(boss_diameter / 2)
    extrude(amount=boss_height)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, block_height / 2) * Cylinder(central_hole_dia / 2, block_height + boss_height + 20)

mount_points = [
    (mount_hole_spacing / 2, mount_hole_spacing / 2),
    (-mount_hole_spacing / 2, mount_hole_spacing / 2),
    (-mount_hole_spacing / 2, -mount_hole_spacing / 2),
    (mount_hole_spacing / 2, -mount_hole_spacing / 2),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, block_height / 2) * Cylinder(mount_hole_dia / 2, block_height + boss_height + 20)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

pocket = Pos(0, -block_width / 2 + pocket_depth / 2, block_height / 2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, block_height - counterbore_depth / 2) * Cylinder(counterbore_dia / 2, counterbore_depth)

part = solid_body
part.name = "block_with_boss_and_holes"
export_step(part, "output.step")
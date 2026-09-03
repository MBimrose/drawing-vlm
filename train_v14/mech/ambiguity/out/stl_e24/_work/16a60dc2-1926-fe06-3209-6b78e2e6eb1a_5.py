from build123d import *

outer_diameter = 60.0
thickness = 13.0
central_hole_diameter = 12.0
central_hole_depth = 10.0
mount_hole_diameter = 4.0
mount_hole_offset = 20.0
chamfer_size = 1.0
boss_diameter = 12.0
boss_height = 8.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, thickness - central_hole_depth / 2) * Cylinder(central_hole_diameter / 2, central_hole_depth)

mount_points = [
    (mount_hole_offset, mount_hole_offset),
    (-mount_hole_offset, mount_hole_offset),
    (-mount_hole_offset, -mount_hole_offset),
    (mount_hole_offset, -mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(mount_hole_diameter / 2, thickness)

part = solid_body
part.name = "flanged_disc_with_holes"
export_step(part, "output.step")
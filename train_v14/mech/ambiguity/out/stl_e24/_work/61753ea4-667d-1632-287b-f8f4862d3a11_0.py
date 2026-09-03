from build123d import *
import math

outer_diameter = 80.0
thickness = 10.0
pocket_diameter = 30.0
pocket_depth = 6.0
slot_length = 70.0
slot_width = 5.0
chamfer_size = 1.0
mount_hole_diameter = 4.0
mount_hole_spacing = 50.0
boss_diameter = 20.0
boss_height = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=thickness)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, thickness - pocket_depth / 2) * Cylinder(pocket_diameter / 2, pocket_depth)

for i in range(3):
    angle = math.radians(i * 120)
    px = (mount_hole_spacing / 2) * math.cos(angle)
    py = (mount_hole_spacing / 2) * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness / 2) * Cylinder(mount_hole_diameter / 2, thickness)

solid_body = solid_body - Pos(0, 0, thickness / 2) * Box(slot_length, slot_width, thickness)

solid_body = solid_body + Pos(0, 0, boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "flanged_disc_with_pocket"
export_step(part, "output.step")
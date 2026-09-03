from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 20.0
boss_diameter = 20.0
boss_height = 5.0
hole_diameter = 8.5
countersink_diameter = 13.0
countersink_angle = 82.0
hole_spacing = 20.0
chamfer_size = 0.8
rib_width = 6.0
rib_height = 4.0
rib_offset = 10.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body + Pos(0, 0, thickness - boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + Pos(rib_offset, 0, thickness - rib_height / 2) * Box(rib_width, rib_height, rib_height)
solid_body = solid_body - Pos(0, 0, thickness - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)

csk_depth = (countersink_diameter / 2 - hole_diameter / 2) / math.tan(math.radians(countersink_angle / 2))
for x in [-hole_spacing / 2, hole_spacing / 2]:
    solid_body = solid_body - Pos(x, 0, thickness / 2) * Cylinder(hole_diameter / 2, thickness + 1)
    solid_body = solid_body - Pos(x, 0, thickness - csk_depth / 2) * Cone(hole_diameter / 2, countersink_diameter / 2, csk_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "flanged_disc_with_boss"
export_step(part, "output.step")
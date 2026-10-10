from build123d import *

leaf_length = 80.0
leaf_width = 32.0
leaf_thickness = 8.0
boss_radius = 8.0
boss_height = 24.0
boss_offset = leaf_length/2 - boss_radius - 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        SlotOverall(leaf_length, leaf_width)
    extrude(amount=leaf_thickness)

solid_body = p.part
solid_body = solid_body + Pos(-boss_offset, 0, leaf_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + Pos(boss_offset, 0, -boss_height/2) * Cylinder(boss_radius, boss_height)

part = solid_body
part.name = "leaf_with_bosses"
export_step(part, "output.step")
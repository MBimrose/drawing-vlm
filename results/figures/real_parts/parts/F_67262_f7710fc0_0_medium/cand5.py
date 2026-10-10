from build123d import *

plate_length = 80.0
plate_width = 32.0
plate_thickness = 8.0
boss_radius = 8.0
boss_height = 24.0
boss_offset = plate_length/2 - boss_radius - 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        SlotOverall(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = solid_body + Pos(-boss_offset, 0, plate_thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + Pos(boss_offset, 0, -boss_height/2) * Cylinder(boss_radius, boss_height)

part = solid_body
part.name = "plate_with_bosses"
export_step(part, "output.step")
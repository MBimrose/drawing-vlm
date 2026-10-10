from build123d import *

leg_length = 80.0
leg_width = 15.0
thickness = 8.0
boss_diameter = 30.0
boss_height = 20.0
boss_hole_diameter = 10.0
hole_diameter = 5.0
hole_spacing = 20.0
hole_offset = 10.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, leg_width),
                     (leg_width, leg_width), (leg_width, leg_length),
                     (0, leg_length), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

boss = Pos(leg_width, leg_width, thickness + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

boss_hole = Pos(leg_width, leg_width, (thickness + boss_height) / 2) * Cylinder(boss_hole_diameter / 2, thickness + boss_height + 10)
solid_body = solid_body - boss_hole

for i in range(3):
    x = leg_width + hole_offset + i * hole_spacing
    y = 0
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(hole_diameter / 2, thickness + 10)

for i in range(3):
    x = 0
    y = leg_width + hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(hole_diameter / 2, thickness + 10)

solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "L_bracket_with_boss"
export_step(part, "output.step")
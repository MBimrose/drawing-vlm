from build123d import *

leg_length = 80.0
leg_width = 15.0
thickness = 8.0
boss_diameter = 30.0
boss_height = 20.0
boss_hole_diameter = 10.0
mount_hole_diameter = 5.0
mount_hole_offset = 20.0

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

boss_hole = Pos(leg_width, leg_width, thickness + boss_height / 2) * Cylinder(boss_hole_diameter / 2, thickness + boss_height + 10)
solid_body = solid_body - boss_hole

mount_hole1 = Pos(leg_length - mount_hole_offset, 0, thickness / 2) * Cylinder(mount_hole_diameter / 2, thickness + 10)
solid_body = solid_body - mount_hole1

mount_hole2 = Pos(0, leg_length - mount_hole_offset, thickness / 2) * Cylinder(mount_hole_diameter / 2, thickness + 10)
solid_body = solid_body - mount_hole2

part = solid_body
part.name = "L_bracket_with_boss"
export_step(part, "output.step")
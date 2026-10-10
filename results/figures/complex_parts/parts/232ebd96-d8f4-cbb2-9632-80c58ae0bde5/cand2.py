from build123d import *

leg_length = 80.0
leg_width = 15.0
thickness = 8.0
boss_diameter = 30.0
boss_height = 20.0
through_hole_diameter = 10.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
pocket_width = 20.0
pocket_depth = 10.0
pocket_height = 4.0
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

through_hole = Pos(leg_width, leg_width, (thickness + boss_height) / 2) * Cylinder(through_hole_diameter / 2, thickness + boss_height + 2)
solid_body = solid_body - through_hole

for i in range(2):
    y_pos = leg_length / 2 + (i - 0.5) * mount_hole_spacing
    hole = Pos(0, y_pos, thickness / 2) * Cylinder(mount_hole_diameter / 2, thickness + 2)
    solid_body = solid_body - hole

for i in range(2):
    x_pos = leg_length / 2 + (i - 0.5) * mount_hole_spacing
    hole = Pos(x_pos, 0, thickness / 2) * Cylinder(mount_hole_diameter / 2, thickness + 2)
    solid_body = solid_body - hole

pocket = Pos(leg_length / 2, leg_width / 2, thickness - pocket_height / 2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - pocket

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")
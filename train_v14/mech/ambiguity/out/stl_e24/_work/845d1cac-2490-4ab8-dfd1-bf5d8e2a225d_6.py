from build123d import *

lever_length = 80.0
base_width = 15.0
tip_width = 8.0
thickness = 6.0
boss_diameter = 12.0
boss_length = 20.0
pocket_width = 15.0
pocket_depth = 3.0
pocket_offset = 30.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_start_offset = 20.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, -base_width/2), (0, base_width/2), (lever_length, tip_width/2), (lever_length, -tip_width/2), close=True)
        make_face()
    extrude(amount=thickness)

solid_body = p.part

boss = Pos(lever_length, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_length)
solid_body = solid_body + boss

pocket = Pos(pocket_offset, thickness/2 - pocket_depth/2, thickness/2) * Box(pocket_width, pocket_depth, thickness)
solid_body = solid_body - pocket

for i in range(3):
    x = hole_start_offset + i * hole_spacing
    hole = Pos(x, 0, thickness/2) * Cylinder(hole_diameter/2, thickness)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "lever"
export_step(part, "output.step")
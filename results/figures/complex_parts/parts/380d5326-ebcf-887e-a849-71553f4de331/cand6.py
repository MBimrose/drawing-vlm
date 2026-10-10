from build123d import *

arm_length = 80.0
arm_diameter_small = 20.0
arm_diameter_large = 30.0
wall_thickness = 3.0
boss_diameter = 12.0
boss_height = 20.0
boss_hole_diameter = 4.0
chamfer_distance = 1.0
pocket_width = 10.0
pocket_height = 8.0
pocket_depth = 5.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(arm_diameter_small / 2)
    with BuildSketch(Plane.XY.offset(arm_length)) as s2:
        Circle(arm_diameter_large / 2)
    loft()

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

boss_center_x = (arm_diameter_small / 2) + (boss_diameter / 2)
boss = Pos(boss_center_x, 0, arm_length / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

hole = Pos(boss_center_x, 0, arm_length / 2) * Cylinder(boss_hole_diameter / 2, boss_height + 2)
solid_body = solid_body - hole

pocket = Pos(0, 0, arm_length / 2 - pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

solid_body = chamfer(solid_body.edges(), chamfer_distance)

part = solid_body
part.name = "tapered_arm_with_boss"
export_step(part, "output.step")
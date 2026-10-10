from build123d import *

arm_length = 80.0
base_radius = 10.0
top_radius = 15.0
wall_thickness = 2.0
boss_radius = 6.0
boss_height = 20.0
boss_offset = 5.0
hole_diameter = 4.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(arm_length)) as s2:
        Circle(top_radius)
    loft()

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

boss_center_x = base_radius + boss_offset + boss_radius
boss_center_z = arm_length / 2.0
boss = Pos(boss_center_x, 0, boss_center_z) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

hole = Pos(boss_center_x, 0, boss_center_z) * Cylinder(hole_diameter / 2, boss_height + 2)
solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges(), chamfer_distance)

part = solid_body
part.name = "lofted_arm_with_boss"
export_step(part, "output.step")
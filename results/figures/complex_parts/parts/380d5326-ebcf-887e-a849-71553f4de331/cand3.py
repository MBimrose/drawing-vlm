from build123d import *

arm_length = 80.0
base_radius = 10.0
top_radius = 15.0
wall_thickness = 2.0
boss_radius = 6.0
boss_height = 20.0
boss_offset = 30.0
hole_diameter = 4.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (base_radius, 0))
            l2 = Line(l1 @ 1, (top_radius, arm_length))
            l3 = Line(l2 @ 1, (0, arm_length))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

boss = Pos(base_radius + boss_radius, 0, boss_offset + boss_height / 2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

hole = Pos(base_radius + boss_radius, 0, arm_length / 2) * Cylinder(hole_diameter / 2, arm_length)
solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges(), chamfer_distance)

part = solid_body
part.name = "revolved_arm_with_boss"
export_step(part, "output.step")
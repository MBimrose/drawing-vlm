from build123d import *

arm_length = 80.0
outer_radius_start = 10.0
outer_radius_end = 15.0
wall_thickness = 2.0
boss_diameter = 12.0
boss_height = 20.0
boss_hole_diameter = 4.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius_start, 0), (outer_radius_end, arm_length))
            l2 = Line(l1 @ 1, (outer_radius_end - wall_thickness, arm_length))
            l3 = Line(l2 @ 1, (outer_radius_start - wall_thickness, 0))
            l4 = Line(l3 @ 1, (outer_radius_start, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

boss = Pos(outer_radius_end + boss_height / 2, 0, arm_length / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

hole = Pos(outer_radius_end + boss_height / 2, 0, arm_length / 2) * Cylinder(boss_hole_diameter / 2, boss_height + 2)
solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "hollow_arm_with_boss"
export_step(part, "output.step")
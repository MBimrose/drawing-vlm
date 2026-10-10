from build123d import *

arm_length = 80.0
outer_radius_start = 10.0
outer_radius_end = 15.0
wall_thickness = 2.0
boss_diameter = 12.0
boss_height = 20.0
boss_offset = 30.0
hole_diameter = 4.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(outer_radius_start)
    with BuildSketch(Plane.XY.offset(arm_length)) as s2:
        Circle(outer_radius_end)
    loft()

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

boss = Pos(outer_radius_end + boss_height/2, 0, boss_offset + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

hole = Pos(outer_radius_end + boss_height/2, 0, boss_offset + boss_height/2) * Cylinder(hole_diameter/2, boss_height + 20)
solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges(), chamfer_distance)

part = solid_body
part.name = "lofted_arm_with_boss"
export_step(part, "output.step")
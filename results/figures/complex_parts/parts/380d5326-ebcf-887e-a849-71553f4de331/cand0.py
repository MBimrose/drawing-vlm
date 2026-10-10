from build123d import *

tube_length = 80.0
start_diameter = 20.0
end_diameter = 28.0
wall_thickness = 2.0
boss_diameter = 12.0
boss_length = 20.0
boss_hole_diameter = 4.0
chamfer_size = 1.0

start_radius = start_diameter / 2.0
end_radius = end_diameter / 2.0
boss_radius = boss_diameter / 2.0
boss_center_radius = (start_radius + end_radius) / 2.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(start_radius)
    with BuildSketch(Plane.XY.offset(tube_length)) as s2:
        Circle(end_radius)
    loft()

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

boss = Pos(boss_center_radius, 0, tube_length / 2.0) * Cylinder(boss_radius, boss_length)
solid_body = solid_body + boss

hole = Pos(boss_center_radius, 0, tube_length / 2.0) * Cylinder(boss_hole_diameter / 2.0, boss_length + 2.0)
solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "tapered_tube_with_boss"
export_step(part, "output.step")
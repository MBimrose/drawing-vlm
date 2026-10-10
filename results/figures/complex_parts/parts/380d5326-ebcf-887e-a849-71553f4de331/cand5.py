from build123d import *

tube_length = 80.0
outer_dia_small = 20.0
outer_dia_large = 30.0
wall_thickness = 2.0
boss_dia = 12.0
boss_length = 20.0
boss_hole_dia = 4.0
chamfer_size = 1.0

outer_radius_small = outer_dia_small / 2.0
outer_radius_large = outer_dia_large / 2.0
inner_radius_small = outer_radius_small - wall_thickness
inner_radius_large = outer_radius_large - wall_thickness
boss_radius = boss_dia / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius_small, 0), (outer_radius_large, tube_length))
            l2 = Line(l1@1, (inner_radius_large, tube_length))
            l3 = Line(l2@1, (inner_radius_small, 0))
            l4 = Line(l3@1, (outer_radius_small, 0))
        make_face()
    revolve(axis=Axis.Z)

tube = p.part

boss_center_x = outer_radius_large - wall_thickness / 2.0
boss_center_z = tube_length / 2.0
boss = Pos(boss_center_x, 0, boss_center_z) * Cylinder(boss_radius, boss_length)
boss_hole = Pos(boss_center_x, 0, boss_center_z) * Cylinder(boss_hole_dia / 2.0, boss_length)
boss = boss - boss_hole

result = tube + boss
result = chamfer(result.edges(), chamfer_size)

part = result
part.name = "tapered_tube_with_boss"
export_step(part, "output.step")
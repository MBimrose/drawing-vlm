from build123d import *

outer_diameter = 60
wall_thickness = 5
inner_diameter = outer_diameter - 2 * wall_thickness
length = 80
boss_diameter = 20
boss_height = 6
boss_offset = 10
chamfer_size = 2
pocket_width = 30
pocket_length = 20
pocket_depth = 10
pocket_hole_diameter = 10
pocket_hole_depth = 15

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
boss_radius = boss_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, length))
            l2 = Line(l1 @ 1, (inner_radius, length))
            l3 = Line(l2 @ 1, (inner_radius, 0))
            l4 = Line(l3 @ 1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

boss = Pos(outer_radius + boss_height / 2.0, 0, boss_offset) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

pocket = Pos(0, 0, length - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)
solid_body = solid_body - pocket

hole = Pos(0, 0, length - pocket_hole_depth / 2) * Cylinder(pocket_hole_diameter / 2.0, pocket_hole_depth)
solid_body = solid_body - hole

part = solid_body
part.name = "hollow_cylinder_with_boss_and_pocket"
export_step(part, "output.step")
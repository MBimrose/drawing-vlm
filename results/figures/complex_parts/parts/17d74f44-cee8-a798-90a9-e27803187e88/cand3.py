from build123d import *

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
length = 80.0
pocket_width = 20.0
pocket_height = 10.0
pocket_depth = 2.0
hole_diameter = 6.0
hole_depth = 8.0
chamfer_size = 0.5
boss_radius = 6.0
boss_height = 8.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, length))
            l3 = Line(l2@1, (inner_radius, length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

pocket = Pos(outer_radius - pocket_depth/2, 0, length/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

hole = Pos(outer_radius - hole_depth/2, -hole_depth/2, length/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
solid_body = solid_body - hole

boss = Pos(inner_radius + boss_height/2, -boss_height/2, length/2) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "hollow_cylinder_with_pocket_hole_boss"
export_step(part, "output.step")
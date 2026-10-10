from build123d import *

outer_radius = 30.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
body_height = 80.0
boss_radius = 10.0
boss_height = 6.0
boss_offset_z = 10.0
chamfer_distance = 2.0
hole_diameter = 8.0
pocket_width = 12.0
pocket_height = 20.0
pocket_depth = 4.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, body_height))
            l3 = Line(l2@1, (inner_radius, body_height))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

boss = Pos(outer_radius + boss_height/2, 0, boss_offset_z) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

solid_body = solid_body - Pos(0, 0, body_height/2) * Cylinder(hole_diameter/2, body_height + 10)

pocket = Pos(outer_radius - pocket_depth/2, 0, body_height/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

part = solid_body
part.name = "hollow_cylinder_with_boss"
export_step(part, "output.step")
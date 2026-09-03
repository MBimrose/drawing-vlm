from build123d import *

outer_radius = 30
wall_thickness = 5
inner_radius = outer_radius - wall_thickness
length = 80
boss_radius = 10
boss_height = 15
boss_offset = 10
chamfer_size = 2

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((inner_radius, 0), (inner_radius, length), (outer_radius, length), (outer_radius, 0), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

boss = Pos(outer_radius + boss_height/2, 0, boss_offset) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "hollow_cylinder_with_boss"
export_step(part, "output.step")
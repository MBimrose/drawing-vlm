from build123d import *

outer_diameter = 60.0
wall_thickness = 5.0
length = 80.0
thread_pitch = 5.0
thread_depth = 2.0
chamfer_size = 2.0
boss_diameter = 20.0
boss_height = 6.0
boss_offset = 10.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
thread_radius = inner_radius - thread_depth

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, length))
            l2 = Line(l1@1, (inner_radius, length))
            l3 = Line(l2@1, (inner_radius, 0))
            l4 = Line(l3@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

boss = Pos(outer_radius + boss_height/2, 0, boss_offset) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

thread_cyl = Pos(0, 0, length/2) * Cylinder(thread_radius, length)
solid_body = solid_body - thread_cyl

part = solid_body
part.name = "threaded_tube_with_boss"
export_step(part, "output.step")
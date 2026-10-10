from build123d import *
import math

outer_radius = 30.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
length = 80.0
chamfer_size = 2.0
thread_pitch = 2.0
thread_depth = 1.0
thread_turns = int(length / thread_pitch)
thread_angle = 360 * thread_turns
boss_radius = 10.0
boss_height = 6.0
boss_offset_z = 12.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, length))
            l2 = Line(l1@1, (outer_radius, length))
            l3 = Line(l2@1, (outer_radius, 0))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

boss = Pos(outer_radius + boss_height/2, 0, boss_offset_z) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

with BuildPart() as tp:
    with BuildSketch(Plane.XZ) as tsk:
        with BuildLine() as tbl:
            tl1 = Line((inner_radius - thread_depth, 0), (inner_radius, 0))
            tl2 = Line(tl1@1, (inner_radius - thread_depth, thread_pitch/2))
            tl3 = Line(tl2@1, (inner_radius - thread_depth, 0))
        make_face()
    extrude(amount=length, taper=thread_angle)

thread_cut = tp.part
solid_body = solid_body - thread_cut

part = solid_body
part.name = "threaded_tube_with_boss"
export_step(part, "output.step")
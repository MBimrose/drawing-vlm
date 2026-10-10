from build123d import *
import math

body_length = 60.0
body_outer_dia = 40.0
body_inner_dia = 30.0
flange_thickness = 10.0
flange_outer_dia = 60.0
mount_hole_dia = 4.0
mount_hole_count = 4
thread_dia = 12.0
thread_length = 30.0
chamfer_size = 2.0
side_port_dia = 6.0
side_port_offset = 12.0

body_outer_radius = body_outer_dia / 2.0
body_inner_radius = body_inner_dia / 2.0
flange_outer_radius = flange_outer_dia / 2.0
wall_thickness = body_outer_radius - body_inner_radius

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((body_inner_radius, 0), (body_outer_radius, 0))
            l2 = Line(l1 @ 1, (body_outer_radius, body_length - flange_thickness))
            l3 = Line(l2 @ 1, (flange_outer_radius, body_length - flange_thickness))
            l4 = Line(l3 @ 1, (flange_outer_radius, body_length))
            l5 = Line(l4 @ 1, (body_inner_radius, body_length))
            l6 = Line(l5 @ 1, (body_inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

hole_r = flange_outer_radius - wall_thickness / 2.0
for i in range(mount_hole_count):
    a = math.radians(i * 360.0 / mount_hole_count)
    solid_body = solid_body - Pos(hole_r * math.cos(a), hole_r * math.sin(a), body_length / 2) * Cylinder(mount_hole_dia / 2, body_length + 10)

solid_body = solid_body - Pos(0, side_port_offset, body_length / 2) * Rot(0, 90, 0) * Cylinder(side_port_dia / 2, body_outer_dia + 10)
solid_body = solid_body - Pos(0, 0, thread_length / 2) * Cylinder(thread_dia / 2, thread_length)

part = solid_body
part.name = "hollow_cylinder_with_flange"
export_step(part, "output.step")
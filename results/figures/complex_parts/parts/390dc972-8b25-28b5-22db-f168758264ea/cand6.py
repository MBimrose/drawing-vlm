from build123d import *
import math

body_length = 60.0
body_outer_dia = 40.0
wall_thickness = 5.0
flange_thickness = 10.0
flange_outer_dia = 60.0
chamfer_size = 2.0
groove_width = 8.0
groove_depth = 3.0
groove_position = 30.0
side_hole_dia = 6.0
side_hole_offset = 12.0
mount_hole_dia = 4.0
mount_hole_count = 4

body_outer_radius = body_outer_dia / 2.0
body_inner_radius = body_outer_radius - wall_thickness
flange_outer_radius = flange_outer_dia / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((body_inner_radius, 0), (body_outer_radius, 0))
            l2 = Line(l1 @ 1, (body_outer_radius, body_length))
            l3 = Line(l2 @ 1, (flange_outer_radius, body_length))
            l4 = Line(l3 @ 1, (flange_outer_radius, body_length + flange_thickness))
            l5 = Line(l4 @ 1, (body_inner_radius, body_length + flange_thickness))
            l6 = Line(l5 @ 1, (body_inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

groove_cyl = Pos(0, groove_position, 0) * Rot(0, 90, 0) * Cylinder(groove_width / 2.0, body_inner_radius - groove_depth)
solid_body = solid_body - groove_cyl

side_hole_cyl = Pos(0, side_hole_offset, body_length / 2.0) * Rot(0, 90, 0) * Cylinder(side_hole_dia / 2.0, body_outer_dia)
solid_body = solid_body - side_hole_cyl

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = (flange_outer_radius - wall_thickness / 2.0) * math.cos(angle)
    py = (flange_outer_radius - wall_thickness / 2.0) * math.sin(angle)
    mount_hole = Pos(px, py, (body_length + flange_thickness) / 2.0) * Cylinder(mount_hole_dia / 2.0, body_length + flange_thickness + 20)
    solid_body = solid_body - mount_hole

part = solid_body
part.name = "revolved_body_with_flange"
export_step(part, "output.step")
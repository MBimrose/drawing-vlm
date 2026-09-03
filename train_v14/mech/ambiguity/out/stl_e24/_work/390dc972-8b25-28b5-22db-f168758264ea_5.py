from build123d import *
import math

body_length = 60.0
body_outer_dia = 40.0
body_inner_dia = 30.0
flange_thickness = 10.0
flange_outer_dia = 60.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 5.0
chamfer_size = 2.0
mount_hole_dia = 4.0
mount_hole_count = 4
mount_hole_radius = (flange_outer_dia/2) - 2.5
inlet_dia = 6.0
inlet_offset = 12.0

body_outer_radius = body_outer_dia/2
body_inner_radius = body_inner_dia/2
flange_outer_radius = flange_outer_dia/2

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((body_outer_radius, 0), (body_outer_radius, body_length))
            l2 = Line(l1@1, (flange_outer_radius, body_length))
            l3 = Line(l2@1, (flange_outer_radius, body_length + flange_thickness))
            l4 = Line(l3@1, (body_inner_radius, body_length + flange_thickness))
            l5 = Line(l4@1, (body_inner_radius, 0))
            l6 = Line(l5@1, (body_outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

pocket = Pos(0, 0, body_length + flange_thickness - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    hole = Pos(px, py, (body_length + flange_thickness)/2) * Cylinder(mount_hole_dia/2, body_length + flange_thickness + 10)
    solid_body = solid_body - hole

inlet = Pos(0, inlet_offset, body_length/2) * Rot(0, 90, 0) * Cylinder(inlet_dia/2, body_outer_dia + 10)
solid_body = solid_body - inlet

part = solid_body
part.name = "revolved_body_with_flange"
export_step(part, "output.step")
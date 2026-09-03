from build123d import *
import math

body_length = 60.0
body_diameter = 40.0
flange_diameter = 60.0
flange_thickness = 10.0
bore_diameter = 30.0
set_screw_diameter = 6.0
set_screw_offset = 12.0
chamfer_size = 2.0
mount_hole_diameter = 4.0
mount_hole_count = 4
mount_hole_radius = (flange_diameter/2 + body_diameter/2) / 2

body_radius = body_diameter / 2.0
flange_radius = flange_diameter / 2.0
total_length = body_length + flange_thickness

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (body_radius, 0))
            l2 = Line(l1@1, (body_radius, body_length))
            l3 = Line(l2@1, (flange_radius, body_length))
            l4 = Line(l3@1, (flange_radius, total_length))
            l5 = Line(l4@1, (0, total_length))
            l6 = Line(l5@1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

solid_body = solid_body - Cylinder(bore_diameter/2, total_length * 2)

set_screw = Pos(0, set_screw_offset, body_length/2) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, body_diameter * 2)
solid_body = solid_body - set_screw

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_length/2) * Cylinder(mount_hole_diameter/2, total_length * 2)

part = solid_body
part.name = "revolved_flanged_shaft"
export_step(part, "output.step")
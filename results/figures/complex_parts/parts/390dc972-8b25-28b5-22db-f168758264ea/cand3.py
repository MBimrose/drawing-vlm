from build123d import *
import math

body_diameter = 40.0
body_length = 60.0
flange_diameter = 60.0
flange_thickness = 10.0
wall_thickness = 5.0
chamfer_size = 2.0
mount_hole_diameter = 4.0
mount_hole_count = 4
mount_hole_radius = (flange_diameter / 2) - wall_thickness / 2
side_port_diameter = 6.0
side_port_offset = 12.0

body_radius = body_diameter / 2.0
flange_radius = flange_diameter / 2.0
inner_radius = body_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (body_radius, 0))
            l2 = Line(l1 @ 1, (body_radius, body_length))
            l3 = Line(l2 @ 1, (flange_radius, body_length))
            l4 = Line(l3 @ 1, (flange_radius, body_length + flange_thickness))
            l5 = Line(l4 @ 1, (inner_radius, body_length + flange_thickness))
            l6 = Line(l5 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, body_length + flange_thickness / 2) * Cylinder(mount_hole_diameter / 2, flange_thickness + 2)

side_port = Pos(0, side_port_offset, body_length / 2) * Rot(0, 90, 0) * Cylinder(side_port_diameter / 2, body_diameter + 2)
solid_body = solid_body - side_port

part = solid_body
part.name = "revolved_flanged_body"
export_step(part, "output.step")
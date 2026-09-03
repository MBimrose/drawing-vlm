from build123d import *
import math

body_diameter = 40.0
body_length = 60.0
flange_diameter = 60.0
flange_thickness = 10.0
bore_diameter = 30.0
port_diameter = 6.0
port_offset = 12.0
chamfer_distance = 2.0
mount_hole_diameter = 4.0
mount_hole_count = 4

body_radius = body_diameter / 2.0
flange_radius = flange_diameter / 2.0
bore_radius = bore_diameter / 2.0
port_radius = port_diameter / 2.0
wall_thickness = body_radius - bore_radius
mount_hole_radius = (bore_radius + flange_radius) / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (body_radius, 0))
            l2 = Line(l1 @ 1, (body_radius, body_length))
            l3 = Line(l2 @ 1, (flange_radius, body_length))
            l4 = Line(l3 @ 1, (flange_radius, body_length + flange_thickness))
            l5 = Line(l4 @ 1, (0, body_length + flange_thickness))
            l6 = Line(l5 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

bore = Pos(0, 0, (body_length + flange_thickness) / 2) * Cylinder(bore_radius, body_length + flange_thickness)
solid_body = solid_body - bore

port = Pos(0, port_offset, body_length / 2) * Rot(0, 90, 0) * Cylinder(port_radius, body_diameter + 2)
solid_body = solid_body - port

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    hole = Pos(px, py, body_length + flange_thickness / 2) * Cylinder(mount_hole_diameter / 2, flange_thickness + 2)
    solid_body = solid_body - hole

part = solid_body
part.name = "valve_body"
export_step(part, "output.step")
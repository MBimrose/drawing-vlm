from build123d import *
import math

body_outer_dia = 40.0
body_length = 60.0
flange_dia = 60.0
flange_thickness = 10.0
bore_dia = 30.0
key_width = 8.0
key_depth = 5.0
key_length = 30.0
chamfer_size = 2.0
mount_hole_dia = 4.0
mount_hole_count = 4
mount_hole_radius = (flange_dia/2 + bore_dia/2) / 2
port_dia = 6.0
port_offset = 12.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(body_outer_dia/2)
    extrude(amount=body_length)
    with BuildSketch(Plane.XY.offset(body_length)) as s2:
        Circle(flange_dia/2)
    extrude(amount=flange_thickness)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, (body_length + flange_thickness)/2) * Cylinder(bore_dia/2, body_length + flange_thickness)

keyway = Pos(0, bore_dia/2 + key_depth/2, body_length/2) * Box(key_length, key_depth, key_width)
solid_body = solid_body - keyway

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, body_length + flange_thickness/2) * Cylinder(mount_hole_dia/2, flange_thickness)

port = Pos(0, port_offset, body_length/2) * Rot(0, 90, 0) * Cylinder(port_dia/2, body_outer_dia)
solid_body = solid_body - port

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "cylinder_with_flange"
export_step(part, "output.step")
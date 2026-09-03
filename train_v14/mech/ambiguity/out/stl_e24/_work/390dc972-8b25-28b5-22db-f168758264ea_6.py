from build123d import *
import math

body_diameter = 40.0
body_length = 60.0
flange_diameter = 60.0
flange_thickness = 10.0
bore_diameter = 30.0
port_diameter = 12.0
port_offset = 15.0
chamfer_size = 2.0
mount_hole_diameter = 4.0
mount_hole_count = 4
mount_hole_radius = (flange_diameter / 2) - 2.5
wall_thickness = (body_diameter - bore_diameter) / 2

body = Pos(0, 0, body_length / 2) * Cylinder(body_diameter / 2, body_length)
flange = Pos(0, 0, body_length + flange_thickness / 2) * Cylinder(flange_diameter / 2, flange_thickness)
result = body + flange

bore = Pos(0, 0, (body_length + flange_thickness) / 2) * Cylinder(bore_diameter / 2, body_length + flange_thickness)
result = result - bore

port_cyl = Pos(0, port_offset, body_length / 2) * Rot(0, 90, 0) * Cylinder(port_diameter / 2, body_diameter)
result = result - port_cyl

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    hole = Pos(px, py, body_length + flange_thickness / 2) * Cylinder(mount_hole_diameter / 2, flange_thickness + 2)
    result = result - hole

part = result
part.name = "cylinder_with_flange"
export_step(part, "output.step")
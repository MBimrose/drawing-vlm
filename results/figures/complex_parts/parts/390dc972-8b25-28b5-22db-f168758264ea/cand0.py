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
side_hole_diameter = 6.0
side_hole_offset = 12.0

body = Pos(0, 0, body_length / 2) * Cylinder(body_diameter / 2, body_length)
flange = Pos(0, 0, body_length + flange_thickness / 2) * Cylinder(flange_diameter / 2, flange_thickness)
result = body + flange

inner = Pos(0, 0, (body_length + flange_thickness) / 2) * Cylinder((body_diameter / 2) - wall_thickness, body_length + flange_thickness)
result = result - inner

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    result = result - Pos(px, py, body_length + flange_thickness / 2) * Cylinder(mount_hole_diameter / 2, flange_thickness + 1)

result = result - Pos(0, side_hole_offset, body_length / 2) * Rot(0, 90, 0) * Cylinder(side_hole_diameter / 2, body_diameter + 2)

part = result
part.name = "flanged_pipe_with_holes"
export_step(part, "output.step")
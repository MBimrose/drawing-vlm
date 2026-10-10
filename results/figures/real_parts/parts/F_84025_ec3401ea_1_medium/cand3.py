from build123d import *
import math

base_width = 80.0
base_length = 80.0
base_thickness = 15.0
body_diameter = 50.0
body_height = 45.0
shoulder_diameter = 30.0
shoulder_height = 10.0
wall_thickness = 3.0
chamfer_size = 2.0
mount_hole_diameter = 7.0
mount_hole_count = 6
mount_hole_radius = 35.0

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_length, base_thickness)
body = Pos(0, 0, base_thickness + body_height/2) * Cylinder(body_diameter/2, body_height)
shoulder = Pos(0, 0, base_thickness + body_height + shoulder_height/2) * Cylinder(shoulder_diameter/2, shoulder_height)

solid_body = base + body + shoulder

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = offset(solid_body, amount=-wall_thickness, openings=solid_body.faces())

total_height = base_thickness + body_height + shoulder_height
solid_body = solid_body - Pos(0, 0, total_height/2) * Cylinder(shoulder_diameter/2, total_height)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, total_height/2) * Cylinder(mount_hole_diameter/2, total_height)

part = solid_body
part.name = "hollow_cylinder_with_mount_holes"
export_step(part, "output.step")
from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 2.0
height = 30.0
rib_width = 4.0
rib_height = 10.0
rib_count = 8
mount_hole_diameter = 5.0
mount_hole_count = 4
chamfer_distance = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

rib = Box(rib_width, rib_height, wall_thickness)
rib = Pos(inner_radius - rib_width / 2.0, 0, height / 2.0) * rib

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    solid_body = solid_body + Rot(0, 0, angle) * rib

hole = Cylinder(mount_hole_diameter / 2.0, wall_thickness + 0.1)
hole = Pos(outer_radius - wall_thickness / 2.0, 0, height / 2.0) * Rot(0, 90, 0) * hole

for i in range(mount_hole_count):
    angle = i * 360.0 / mount_hole_count
    solid_body = solid_body - Rot(0, 0, angle) * hole

part = solid_body
part.name = "ribbed_cylinder_with_mount_holes"
export_step(part, "output.step")
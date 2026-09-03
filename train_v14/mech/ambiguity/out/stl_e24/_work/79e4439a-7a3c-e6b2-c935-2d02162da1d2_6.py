from build123d import *
import math

cap_outer_diameter = 80.0
cap_height = 30.0
wall_thickness = 2.0
rib_thickness = 4.0
rib_height = 10.0
rib_count = 8
mount_hole_diameter = 5.0
mount_hole_radius = 34.0
chamfer_distance = 0.5

solid_body = Cylinder(cap_outer_diameter / 2, cap_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

inner_radius = (cap_outer_diameter / 2) - wall_thickness
rib = Pos(inner_radius - rib_thickness / 2, 0, cap_height / 2) * Box(rib_thickness, rib_height, wall_thickness)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    solid_body = solid_body + Rot(0, 0, angle) * rib

for i in range(4):
    angle = i * 90.0
    x = mount_hole_radius * math.cos(math.radians(angle))
    y = mount_hole_radius * math.sin(math.radians(angle))
    hole = Pos(x, y, cap_height / 2) * Rot(0, 90, angle) * Cylinder(mount_hole_diameter / 2, wall_thickness + 0.1)
    solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

part = solid_body
part.name = "ribbed_cap"
export_step(part, "output.step")
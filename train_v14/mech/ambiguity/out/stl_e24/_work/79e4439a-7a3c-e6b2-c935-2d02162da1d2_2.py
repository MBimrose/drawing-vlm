from build123d import *
import math

outer_diameter = 80.0
cap_height = 30.0
wall_thickness = 2.0
recess_diameter = 30.0
recess_depth = 5.0
chamfer_size = 0.5
mount_hole_diameter = 5.0
mount_hole_count = 4
rib_width = 4.0
rib_height = 10.0
rib_count = 8

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
recess_radius = recess_diameter / 2.0
mount_hole_radius = mount_hole_diameter / 2.0
mount_hole_center_radius = outer_radius - wall_thickness / 2.0

solid_body = Cylinder(outer_radius, cap_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

recess = Pos(0, 0, cap_height - recess_depth/2) * Cylinder(recess_radius, recess_depth)
solid_body = solid_body - recess

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for i in range(mount_hole_count):
    angle = i * 360.0 / mount_hole_count
    rad = math.radians(angle)
    x = mount_hole_center_radius * math.cos(rad)
    y = mount_hole_center_radius * math.sin(rad)
    hole = Pos(x, y, cap_height/2) * Rot(0, 90, angle) * Cylinder(mount_hole_radius, wall_thickness + 0.1)
    solid_body = solid_body - hole

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rad = math.radians(angle)
    x = (inner_radius - rib_width/2) * math.cos(rad)
    y = (inner_radius - rib_width/2) * math.sin(rad)
    rib = Pos(x, y, cap_height/2) * Rot(0, 0, angle) * Box(rib_width, rib_height, wall_thickness)
    solid_body = solid_body + rib

part = solid_body
part.name = "cap_with_ribs"
export_step(part, "output.step")
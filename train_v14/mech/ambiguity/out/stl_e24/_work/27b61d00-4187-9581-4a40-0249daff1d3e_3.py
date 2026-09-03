from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 6.0
height = 55.0
recess_depth = 12.0
recess_radius = 30.0
rib_count = 12
rib_thickness = 2.0
rib_height = 12.0
chamfer_size = 1.5

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

recess = Pos(0, 0, height - recess_depth/2) * Cylinder(recess_radius, recess_depth)
solid_body = solid_body - recess

rib_center_radius = inner_radius - rib_thickness / 2.0
rib_length = height - recess_depth - 5.0
for i in range(rib_count):
    angle_deg = i * 360.0 / rib_count
    px = rib_center_radius * math.cos(math.radians(angle_deg))
    py = rib_center_radius * math.sin(math.radians(angle_deg))
    rib = Pos(px, py, rib_length/2) * Rot(0, 0, angle_deg) * Box(rib_thickness, rib_height, rib_length)
    solid_body = solid_body + rib

part = solid_body
part.name = "XMountSocket"
export_step(part, "output.step")
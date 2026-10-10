from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 6.0
height = 50.0
rib_thickness = 2.0
rib_width = 12.0
rib_height = 45.0
rib_count = 12
central_hole_diameter = 30.0
mount_hole_diameter = 5.0
mount_hole_offset = 20.0
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Cylinder(central_hole_diameter / 2, height)

for i in range(4):
    angle = math.radians(i * 90)
    px = mount_hole_offset * math.cos(angle)
    py = mount_hole_offset * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mount_hole_diameter / 2, height)

rib = Pos(inner_radius - rib_thickness / 2.0, 0, rib_height / 2.0) * Box(rib_thickness, rib_width, rib_height)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

part = solid_body + ribs
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")
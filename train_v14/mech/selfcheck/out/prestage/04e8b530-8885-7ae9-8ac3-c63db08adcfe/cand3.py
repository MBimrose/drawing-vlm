from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 70.0
height = 30.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
central_hole_diameter = 20.0
mount_hole_diameter = 5.0
mount_hole_radius = 30.0
rib_thickness = 2.0
rib_width = 3.0
rib_count = 8
chamfer_size = 2.0
groove_depth = 2.0
groove_width = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

solid_body = solid_body - Cylinder(central_hole_diameter / 2.0, height)

for i in range(4):
    angle = math.radians(i * 90.0)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mount_hole_diameter / 2.0, height)

groove_radius = outer_radius - groove_width / 2.0
solid_body = solid_body - Pos(0, 0, height / 2.0 - groove_depth / 2.0) * Cylinder(groove_radius, groove_depth)

rib = Pos(inner_radius - rib_thickness / 2.0, 0, height / 2.0) * Box(rib_thickness, rib_width, height)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")
from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 6.0
height = 55.0
rib_count = 12
rib_width = 8.0
rib_thickness = 2.0
rib_height = 40.0
chamfer_size = 2.0
mount_hole_diameter = 5.0
mount_hole_count = 6
mount_hole_radius = 30.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = fillet(bottom_face.edges(), 0.5)

rib = Pos(inner_radius - rib_thickness/2.0, 0, rib_height/2.0) * Box(rib_thickness, rib_width, rib_height)
ribs = rib
for i in range(1, rib_count):
    ribs = ribs + Rot(0, 0, i * 360.0 / rib_count) * rib

solid_body = solid_body + ribs

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, height/2.0) * Cylinder(mount_hole_diameter/2, height + 10)

part = solid_body
part.name = "ribbed_cylinder_with_mount_holes"
export_step(part, "output.step")
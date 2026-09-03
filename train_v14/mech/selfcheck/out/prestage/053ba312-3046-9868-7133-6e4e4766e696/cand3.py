from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
height = 60.0
rib_count = 6
rib_thickness = 4.0
rib_height = 6.0
central_hole_diameter = 10.0
mount_hole_diameter = 5.0
mount_hole_count = 6
fillet_radius = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)
solid_body = solid_body - Cylinder(central_hole_diameter / 2, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = fillet(bottom_face.edges(), fillet_radius)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = (outer_radius - wall_thickness / 2) * math.cos(angle)
    py = (outer_radius - wall_thickness / 2) * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mount_hole_diameter / 2, height)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius - rib_thickness / 2, 0, 0) * Box(rib_thickness, rib_height, height)
    solid_body = solid_body + rib

part = solid_body
part.name = "ribbed_cylinder_with_holes"
export_step(part, "output.step")
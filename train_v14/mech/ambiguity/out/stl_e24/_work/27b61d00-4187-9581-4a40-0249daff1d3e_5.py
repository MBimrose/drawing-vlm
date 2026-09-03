from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 6.0
length = 60.0
rib_height = 12.0
rib_thickness = 2.0
rib_count = 12
chamfer_distance = 2.0
central_hole_diameter = 12.0
mount_hole_diameter = 6.0
mount_hole_count = 4

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

solid_body = solid_body - Cylinder(central_hole_diameter / 2, length)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = (outer_radius - wall_thickness / 2) * math.cos(angle)
    py = (outer_radius - wall_thickness / 2) * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mount_hole_diameter / 2, length)

for i in range(rib_count):
    angle = math.radians(i * 360.0 / rib_count)
    rib = Rot(0, 0, angle) * Pos(inner_radius - rib_thickness / 2, 0, length / 2) * Box(rib_thickness, rib_height, length)
    solid_body = solid_body + rib

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")
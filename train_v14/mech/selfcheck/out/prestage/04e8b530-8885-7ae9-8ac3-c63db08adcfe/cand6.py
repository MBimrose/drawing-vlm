from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
height = 30.0
base_fillet_radius = 2.0
central_hole_diameter = 10.0
mount_hole_diameter = 5.0
mount_hole_radius = 30.0
rib_thickness = 2.0
rib_width = 3.0
rib_height = 20.0
rib_count = 8

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

result = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)
result = result - Cylinder(central_hole_diameter / 2, height)

for i in range(4):
    a = math.radians(i * 90)
    result = result - Pos(mount_hole_radius * math.cos(a), mount_hole_radius * math.sin(a), 0) * Cylinder(mount_hole_diameter / 2, height)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = fillet(bottom_face.edges(), base_fillet_radius)

rib = Pos(inner_radius - rib_thickness / 2, 0, height / 2) * Box(rib_thickness, rib_width, rib_height)
ribs = rib
for i in range(1, rib_count):
    ribs = ribs + Rot(0, 0, i * 360 / rib_count) * rib

result = result + ribs
part = result
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")
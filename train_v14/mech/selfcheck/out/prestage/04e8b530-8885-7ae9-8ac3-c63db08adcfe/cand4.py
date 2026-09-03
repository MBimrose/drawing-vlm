from build123d import *
import math

outer_diameter = 80
cap_height = 30
wall_thickness = 5
fillet_radius = 2
chamfer_distance = 1
pocket_diameter = 40
pocket_depth = 5
central_hole_diameter = 5
mount_hole_diameter = 3
mount_hole_offset = 20
rib_thickness = 2
rib_height = 3
rib_count = 8

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

result = Cylinder(outer_radius, cap_height) - Cylinder(inner_radius, cap_height)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = fillet(bottom_face.edges(), fillet_radius)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

result = result - Pos(0, 0, cap_height - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)
result = result - Pos(0, 0, cap_height/2) * Cylinder(central_hole_diameter/2, cap_height)

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (-mount_hole_offset, -mount_hole_offset), (mount_hole_offset, -mount_hole_offset)]:
    result = result - Pos(x, y, cap_height/2) * Cylinder(mount_hole_diameter/2, cap_height)

rib = Pos(inner_radius + rib_thickness/2, 0, cap_height/2) * Box(rib_thickness, rib_height, cap_height)
ribs = rib
for i in range(1, rib_count):
    ribs = ribs + Rot(0, 0, i * 360.0 / rib_count) * rib

result = result + ribs

part = result
part.name = "cap_with_ribs"
export_step(part, "output.step")
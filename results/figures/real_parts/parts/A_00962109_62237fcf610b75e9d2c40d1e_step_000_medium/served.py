from build123d import *
import math

overall_width = 80.0
overall_height = 73.2
thickness = 6.6
lobe_radius = 14.8
lobe_center_radius = 29.1
fillet_radius = 1.9
hole_diameter = 21.1
central_hole_diameter = 21.1

lobe_angles = [90, 210, 330]
lobe_positions = [
    (lobe_center_radius * math.cos(math.radians(a)), lobe_center_radius * math.sin(math.radians(a)))
    for a in lobe_angles
]

solid_body = Cylinder(lobe_radius, thickness)
for x, y in lobe_positions:
    solid_body = solid_body + Pos(x, y, 0) * Cylinder(lobe_radius, thickness)

solid_body = fillet(solid_body.edges(), fillet_radius)

solid_body = solid_body - Cylinder(central_hole_diameter / 2, thickness)
for x, y in lobe_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, thickness)

part = solid_body
part.name = "tri_lobe_disc"
export_step(part, "output.step")
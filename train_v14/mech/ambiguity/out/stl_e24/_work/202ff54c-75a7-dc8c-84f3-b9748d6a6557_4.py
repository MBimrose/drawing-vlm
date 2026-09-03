from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
length = 60.0
wall_thickness = (outer_diameter - inner_diameter) / 2
rib_height = 6.0
rib_width = 30.0
rib_thickness = 4.0
rib_count = 4
pocket_width = 20.0
pocket_height = 12.0
pocket_depth = 5.0
chamfer_size = 2.0
hole_diameter = 4.0
hole_spacing = 30.0

outer_radius = outer_diameter / 2
inner_radius = inner_diameter / 2

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

for i in range(rib_count):
    angle = i * 360 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius, 0, 0) * Box(rib_thickness, rib_height, rib_width)
    result = result + rib

pocket = Pos(outer_radius - pocket_depth / 2, 0, 0) * Box(pocket_depth, pocket_height, pocket_width)
result = result - pocket

for x, y in [(-hole_spacing, 0), (hole_spacing, 0)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, length * 2)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")
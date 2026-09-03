from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
length = 60.0
wall_thickness = (outer_diameter - inner_diameter) / 2
rib_height = 6.0
rib_width = 30.0
rib_thickness = 3.0
rib_count = 4
chamfer_size = 2.0
mount_hole_dia = 4.0
mount_hole_spacing = 20.0
pocket_width = 12.0
pocket_depth = 20.0
pocket_height = 8.0

result = Cylinder(outer_diameter / 2, length) - Cylinder(inner_diameter / 2, length)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_diameter / 2 + rib_thickness / 2, 0, 0) * Box(rib_thickness, rib_height, rib_width)
    result = result + rib

hole_r = mount_hole_dia / 2
hole_h = length + 2
for x in [outer_diameter / 2 - wall_thickness / 2, -(outer_diameter / 2 - wall_thickness / 2)]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_r, hole_h)

pocket = Pos(outer_diameter / 2 - pocket_height / 2, 0, 0) * Box(pocket_height, pocket_width, pocket_depth)
result = result - pocket

part = result
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")
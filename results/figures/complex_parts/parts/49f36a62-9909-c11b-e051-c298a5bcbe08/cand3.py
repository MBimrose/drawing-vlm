from build123d import *

outer_diameter = 38.0
inner_diameter = 19.6
height = 15.0
rib_height = 2.0
rib_width = 1.0
pocket_width = 12.0
pocket_length = 8.0
pocket_depth = 2.0
chamfer_distance = 0.4
center_hole_diameter = 4.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

base = Pos(0, 0, height / 2) * Cylinder(outer_radius, height)
base = base - Pos(0, 0, height / 2) * Cylinder(inner_radius, height)

rib = Pos(0, 0, height + rib_height / 2) * Cylinder(outer_radius, rib_height)
rib = rib - Pos(0, 0, height + rib_height / 2) * Cylinder(outer_radius - rib_width, rib_height)

result = base + rib

pocket = Pos(0, 0, height + rib_height - pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)
result = result - pocket

hole = Pos(0, 0, (height + rib_height) / 2) * Cylinder(center_hole_diameter / 2, height + rib_height + 10)
result = result - hole

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "ribbed_cylinder_with_pocket"
export_step(part, "output.step")
from build123d import *

leaf_length = 80.0
leaf_width = 30.0
leaf_thickness = 4.0
rib_width = 20.0
rib_height = 2.0
hole_diameter = 5.0
hole_spacing = 12.0
num_holes = 8
chamfer_distance = 1.0

base = Box(leaf_length, leaf_width, leaf_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

rib = Pos(0, 0, leaf_thickness) * Box(rib_width, rib_width, rib_height)
solid_body = base + rib

hole_positions = [((i - (num_holes - 1) / 2) * hole_spacing, 0) for i in range(num_holes)]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, leaf_thickness + rib_height / 2) * Cylinder(hole_diameter / 2, leaf_thickness + rib_height + 2)

part = solid_body
part.name = "leaf_with_rib_and_holes"
export_step(part, "output.step")
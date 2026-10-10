from build123d import *

total_length = 80.0
bracket_width = 30.0
bracket_thickness = 6.0
sleeve_radius = 12.0
sleeve_length = 60.0
hole_diameter = 5.0
hole_count = 5
hole_spacing = sleeve_length / (hole_count + 1)
fillet_radius = 2.0
chamfer_distance = 1.0
rib_height = 3.0
rib_width = 4.0
rib_spacing = 12.0
rib_count = 4
pocket_width = 20.0
pocket_length = 40.0
pocket_depth = 2.0

import math

result = Box(total_length, bracket_width, bracket_thickness)
result = fillet(result.edges(), fillet_radius)

sleeve = Rot(0, 90, 0) * Cylinder(sleeve_radius, sleeve_length)
result = result + sleeve

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

for i in range(hole_count):
    x = hole_spacing * (i - (hole_count - 1) / 2)
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, 50)

for i in range(rib_count):
    x = rib_spacing * (i - (rib_count - 1) / 2)
    rib = Pos(x, 0, bracket_thickness / 2 + rib_height / 2) * Box(rib_width, bracket_width - 2 * chamfer_distance, rib_height)
    result = result + rib

pocket = Pos(0, 0, -bracket_thickness / 2 + pocket_depth / 2) * Box(pocket_width, pocket_length, pocket_depth)
result = result - pocket

part = result
part.name = "bracket_with_sleeve"
export_step(part, OUTPUT_PATH)
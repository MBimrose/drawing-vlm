from build123d import *
import math

outer_diameter = 30.0
inner_diameter = 12.0
collar_length = 20.0
fin_thickness = 2.0
fin_height = 8.0
set_screw_diameter = 6.0
set_screw_head_diameter = 10.0
set_screw_head_depth = 4.0
chamfer_distance = 0.5
overlap = 0.2

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
set_screw_offset = outer_radius - set_screw_head_depth / 2.0

result = Pos(0, 0, collar_length / 2) * Cylinder(outer_radius, collar_length)
result = result - Pos(0, 0, collar_length / 2) * Cylinder(inner_radius, collar_length)

fin = Pos(outer_radius + fin_height / 2.0 - overlap, 0, 0) * Box(fin_thickness, collar_length, fin_height)
fins = fin
for i in range(1, 3):
    fins = fins + Rot(0, 0, i * 120) * fin
result = result + fins

shaft_hole = Pos(set_screw_offset, 0, collar_length / 2.0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, outer_diameter + 2)
result = result - shaft_hole

cbore_hole = Pos(set_screw_offset, 0, collar_length / 2.0) * Rot(0, 90, 0) * Cylinder(set_screw_head_diameter / 2.0, set_screw_head_depth)
result = result - cbore_hole

part = result
part.name = "collar_with_fins"
export_step(part, "output.step")
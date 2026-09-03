from build123d import *

outer_diameter = 30.0
inner_diameter = 12.0
collar_height = 20.0
fin_height = 8.0
fin_thickness = 2.0
fin_count = 3
set_screw_diameter = 6.0
set_screw_counterbore_diameter = 10.0
set_screw_counterbore_depth = 4.0
slot_width = 4.0
slot_length = 12.0
slot_depth = 2.0
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Pos(0, 0, collar_height / 2) * Cylinder(outer_radius, collar_height)
result = result - Pos(0, 0, collar_height / 2) * Cylinder(inner_radius, collar_height)

fin = Pos(outer_radius + fin_height / 2.0, 0, 0) * Box(fin_thickness, collar_height, fin_height)
fins = fin
for i in range(1, fin_count):
    angle = i * 360.0 / fin_count
    fins = fins + Rot(0, 0, angle) * fin
result = result + fins

result = result - Pos(outer_radius, 0, collar_height / 2) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2, outer_diameter)
result = result - Pos(outer_radius - set_screw_counterbore_depth / 2, 0, collar_height / 2) * Rot(0, 90, 0) * Cylinder(set_screw_counterbore_diameter / 2, set_screw_counterbore_depth)

result = result - Pos(outer_radius - slot_depth / 2, 0, collar_height / 2) * Box(slot_depth, slot_width, slot_length)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "collar_with_fins"
export_step(part, "output.step")
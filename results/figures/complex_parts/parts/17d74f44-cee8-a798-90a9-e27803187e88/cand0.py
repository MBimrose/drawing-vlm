from build123d import *

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
length = 80.0
rib_width = 10.0
rib_height = 12.0
rib_thickness = 2.0
rib_position = 40.0
hole_diameter = 6.0
hole_offset = 8.0
chamfer_size = 0.5
slot_width = 4.0
slot_depth = 2.0
slot_length = 20.0

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

rib = Pos(inner_radius - rib_thickness/2, -rib_height/2, 0) * Rot(0, 90, 0) * Cylinder(rib_height/2, rib_width)
result = result + rib

hole = Pos(outer_radius - wall_thickness/2, -hole_offset, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, wall_thickness + 2)
result = result - hole

slot = Pos(inner_radius - slot_depth/2, 0, 0) * Box(slot_depth, slot_length, slot_width)
result = result - slot

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "hollow_cylinder_with_rib"
export_step(part, "output.step")
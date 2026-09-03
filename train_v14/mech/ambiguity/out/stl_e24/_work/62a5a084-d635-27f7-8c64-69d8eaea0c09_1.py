from build123d import *
import math

outer_diameter = 30.0
inner_diameter = 12.0
length = 20.0
fin_height = 8.0
fin_thickness = 2.0
fin_count = 3
set_screw_diameter = 6.0
set_screw_head_diameter = 10.0
set_screw_head_depth = 4.0
chamfer_size = 0.5
slot_width = 4.0
slot_length = 12.0
slot_depth = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius
fin_length = wall_thickness

result = Pos(0, 0, length/2) * Cylinder(outer_radius, length)
result = result - Pos(0, 0, length/2) * Cylinder(inner_radius, length)

for i in range(fin_count):
    angle = i * 360.0 / fin_count
    fin = Rot(0, 0, angle) * Pos(outer_radius + fin_length/2.0, 0, 0) * Box(fin_thickness, length, fin_height)
    result = result + fin

set_screw_cyl = Pos(outer_radius - wall_thickness/2.0, 0, length/2.0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2.0, wall_thickness + 2.0)
result = result - set_screw_cyl

counterbore = Pos(outer_radius - set_screw_head_depth/2.0, 0, length/2.0) * Rot(0, 90, 0) * Cylinder(set_screw_head_diameter/2.0, set_screw_head_depth)
result = result - counterbore

slot = Pos(outer_radius - slot_depth/2.0, 0, length/2.0) * Box(slot_depth, slot_width, slot_length)
result = result - slot

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "finned_cylinder_with_set_screw"
export_step(part, "output.step")
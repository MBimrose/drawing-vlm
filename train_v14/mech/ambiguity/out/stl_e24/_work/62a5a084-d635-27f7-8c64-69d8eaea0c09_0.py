from build123d import *
import math

outer_diameter = 30.0
inner_diameter = 12.0
collar_length = 20.0
rib_thickness = 2.0
rib_height = 8.0
rib_count = 3
set_screw_diameter = 6.0
set_screw_head_diameter = 10.0
set_screw_head_depth = 4.0
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Pos(0, 0, collar_length/2) * Cylinder(outer_radius, collar_length)
result = result - Pos(0, 0, collar_length/2) * Cylinder(inner_radius, collar_length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_thickness/2.0, 0, 0) * Box(rib_thickness, collar_length, rib_height)
    result = result + rib

set_screw_hole = Pos(outer_radius, 0, collar_length/2.0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2.0, outer_diameter)
result = result - set_screw_hole

counterbore = Pos(outer_radius - set_screw_head_depth/2.0, 0, collar_length/2.0) * Rot(0, 90, 0) * Cylinder(set_screw_head_diameter/2.0, set_screw_head_depth)
result = result - counterbore

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "collar_with_ribs"
export_step(part, "output.step")
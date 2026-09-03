from build123d import *

outer_diameter = 30.0
inner_diameter = 12.0
length = 20.0
rib_thickness = 2.0
rib_height = 8.0
rib_count = 3
set_screw_diameter = 6.0
set_screw_head_diameter = 10.0
set_screw_head_depth = 4.0
slot_width = 4.0
slot_length = 12.0
slot_depth = 6.0
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Pos(0, 0, length/2) * Cylinder(outer_radius, length)
result = result - Pos(0, 0, length/2) * Cylinder(inner_radius, length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_thickness/2.0, 0, 0) * Box(rib_thickness, length, rib_height)
    result = result + rib

result = result - Pos(outer_radius - set_screw_head_depth/2.0, 0, length/2.0) * Rot(0, 90, 0) * Cylinder(set_screw_head_diameter/2.0, set_screw_head_depth)
result = result - Pos(outer_radius, 0, length/2.0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2.0, outer_diameter)

result = result - Pos(outer_radius - slot_depth/2.0, 0, length/2.0) * Box(slot_depth, slot_width, slot_length)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "ribbed_shaft_with_set_screw"
export_step(part, "output.step")
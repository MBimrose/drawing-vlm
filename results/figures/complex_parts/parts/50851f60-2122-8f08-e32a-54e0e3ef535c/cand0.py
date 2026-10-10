from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 30.0
collar_height = 20.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
groove_width = 4.0
groove_depth = 2.0
slot_width = 4.0
slot_depth = wall_thickness - 2.0
slot_count = 4
set_screw_diameter = 4.0
set_screw_offset = 10.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, collar_height) - Cylinder(inner_radius, collar_height)

groove = Pos(0, 0, collar_height/2 - groove_depth/2) * Cylinder(inner_radius - groove_width/2, groove_depth)
result = result - groove

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, collar_height * 0.6)
    result = result - slot

set_screw = Pos(set_screw_offset, 0, collar_height/2) * Cylinder(set_screw_diameter/2, collar_height)
result = result - set_screw

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "collar_with_groove_slots"
export_step(part, "output.step")
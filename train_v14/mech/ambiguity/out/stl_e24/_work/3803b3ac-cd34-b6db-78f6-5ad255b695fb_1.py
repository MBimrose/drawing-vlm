from build123d import *

base_width = 80.0
base_depth = 30.0
base_thickness = 6.0
boss_radius = 12.0
boss_height = 5.0
chamfer_size = 0.5
hole_diameter = 4.0
hole_offset_x = 20.0
hole_offset_y = 6.0
slot_width = 6.0
slot_length = 20.0

result = Box(base_width, base_depth, base_thickness)

for x, y in [(-hole_offset_x, -hole_offset_y), (-hole_offset_x, hole_offset_y),
             (hole_offset_x, -hole_offset_y), (hole_offset_x, hole_offset_y)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, base_thickness + 1)

result = result - Pos(-base_width/2 + slot_width/2, 0, 0) * Box(slot_width, slot_length, base_thickness + 1)
result = result - Pos(base_width/2 - slot_width/2, 0, 0) * Box(slot_width, slot_length, base_thickness + 1)

result = result + Pos(0, 0, base_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "base_plate_with_boss"
export_step(part, "output.step")
from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
gear_width = 20.0
tooth_height = 5.0
tooth_width = 6.0
num_teeth = 20
chamfer_size = 0.5
set_screw_diameter = 2.0
set_screw_offset = 22.0
slot_width = 4.0
slot_length = gear_width * 0.8

result = Cylinder(outer_diameter / 2, gear_width)
result = result - Cylinder(inner_diameter / 2, gear_width)

for i in range(num_teeth):
    angle = i * 360.0 / num_teeth
    tooth = Rot(0, 0, angle) * Pos(outer_diameter / 2, 0, gear_width / 2) * Box(tooth_width, tooth_height, gear_width)
    result = result + tooth

result = result - Pos(set_screw_offset, 0, 0) * Cylinder(set_screw_diameter / 2, gear_width * 2)
result = result - Pos(inner_diameter / 2, 0, gear_width / 2) * Box(slot_width, slot_length, gear_width * 1.2)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "gear_with_teeth"
export_step(part, "output.step")
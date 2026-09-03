from build123d import *

outer_diameter = 60.0
inner_diameter = 30.0
collar_length = 20.0
keyway_width = 6.0
keyway_depth = 8.0
slot_width = 4.0
slot_length = 12.0
slot_depth = (outer_diameter - inner_diameter) / 2.0
chamfer_size = 1.0
relief_width = 30.0
relief_height = 10.0
relief_depth = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

result = Cylinder(outer_radius, collar_length) - Cylinder(inner_radius, collar_length)

keyway = Pos(0, 0, collar_length - keyway_depth / 2) * Box(keyway_width, collar_length, keyway_depth)
result = result - keyway

for angle in [0, 90, 180, 270]:
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth / 2, 0, 0) * Box(slot_depth, slot_width, slot_length)
    result = result - slot

relief = Pos(0, 0, collar_length - relief_depth / 2) * Box(relief_width, relief_height, relief_depth)
result = result - relief

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "collar_with_keyway_and_slots"
export_step(part, "output.step")
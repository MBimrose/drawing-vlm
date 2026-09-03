from build123d import *

outer_diameter = 80.0
outer_radius = outer_diameter / 2.0
plate_thickness = 5.0
hub_diameter = 20.0
hub_radius = hub_diameter / 2.0
hub_height = 3.0
slot_width = 5.0
slot_length = outer_radius - hub_radius - 5.0
num_slots = 6
chamfer_size = 0.5
pocket_depth = 2.0
pocket_radius = hub_radius - 3.0

base = Cylinder(outer_radius, plate_thickness)
hub = Cylinder(hub_radius, hub_height)
result = base + hub

slot_center_x = hub_radius + slot_length / 2.0
slot_body = Pos(slot_center_x, 0, plate_thickness / 2) * Box(slot_length, slot_width, plate_thickness)
slots = slot_body
for i in range(1, num_slots):
    angle = i * 360.0 / num_slots
    rotated_slot = Rot(0, 0, angle) * slot_body
    slots = slots + rotated_slot

result = result - slots

pocket = Pos(0, 0, plate_thickness - pocket_depth / 2) * Cylinder(pocket_radius, pocket_depth)
result = result - pocket

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_hub_and_slots"
export_step(part, "output.step")